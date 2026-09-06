import json
import uuid
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

from common.common import CommonData
from common.config import CHUNK_DIR
from jobs_queue.queue import AudioQueue
from log.loggerService import LoggerService
from models.AudioAsset import AudioAsset
from models.Job import Job
from models.TTSTranscription import TTSTranscription
from models.chunk import Chunk
from models.chunk_audio import ChunkAudio, ChunkWord
from models.enum.BookStatus import BookStatus
from models.mediaManifest import MediaManifest
from models.wordLevelTranscription import WordLevelTranscription
from storage.JobRepository.jobRepositoryProvider import JobRepositoryProvider
from storage.audioAssetRepository.audioAssetRepositoryProvider import (
    AudioAssetRepositoryProvider,
)
from storage.bucket.bucketProvider import BucketProvider
from storage.bucket.impl.bucketProviderImpl import BucketProviderImpl
from storage.chunkRepository.chunkRepositoryProvider import ChunkRepositoryProvider
from storage.mediaManifestRepository.mediaManifestRepositoryProvider import MediaManifestRepositoryProvider
from tts.TTSProvider import TTSProvider
from word_level.word_level_provider import WordLevelProvider



class AudioWorker:

    def __init__(
        self,
        queue: AudioQueue,
        jobs: JobRepositoryProvider,
        chunks: ChunkRepositoryProvider,
        audio_service: TTSProvider,
        word_level_service: WordLevelProvider,
        bucket: BucketProvider,
        audio_asset: AudioAssetRepositoryProvider,
        media_manifest: MediaManifestRepositoryProvider,
    ):
        self._queue = queue
        self._jobs = jobs
        self.chunks = chunks
        self.audio_service = audio_service
        self.word_level_service = word_level_service
        self.bucket = bucket
        self.audio_asset = audio_asset
        self.media_manifest = media_manifest

        LoggerService.log_info("AudioWorker initialized successfully")

    def generate_chunk_id_json(
        self,
        word_level: WordLevelTranscription,
        chunk_id: str,
    ) -> None:
        LoggerService.log_info(
            "Starting JSON generation for chunk_id: %s",
            chunk_id,
        )

        if not word_level.segments:
            error_msg = f"None segment found for chunk_id: {chunk_id}"

            LoggerService.log_error("Failed to generate JSON for chunk_id: %s - %s",chunk_id,error_msg,)

            raise ValueError(error_msg)

        first_segment = word_level.segments[0]
        last_segment = word_level.segments[-1]

        LoggerService.log_debug("Chunk %s has %s segments. First: %s-%s, Last: %s-%s",
            chunk_id,len(word_level.segments),first_segment["start"],first_segment["end"],last_segment["start"],last_segment["end"],)

        chunk_audio = ChunkAudio(
            start=float(first_segment["start"]),
            end=float(last_segment["end"]),
            words=[],
        )

        word_count = 0

        for segment in word_level.segments:
            for word in segment["words"]:
                chunk_audio.words.append(
                    ChunkWord(
                        text=word["word"],
                        start=float(word["start"]),
                        end=float(word["end"]),
                    )
                )
                word_count += 1

        LoggerService.log_debug("Chunk %s has %s words processed",chunk_id,word_count,)

        CHUNK_DIR.mkdir(exist_ok=True)

        file_path = str(CHUNK_DIR / f"{chunk_id}.json")

        try:
            with open(
                file_path,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    asdict(chunk_audio),
                    file,
                    ensure_ascii=False,
                    indent=2,
                )

            LoggerService.log_info("Generated chunk JSON for chunk_id: %s at path: %s",chunk_id,file_path,)

            LoggerService.log_debug("JSON file size for chunk_id %s: %s bytes",chunk_id,
                Path(file_path).stat().st_size,)

        except Exception as exc:
            LoggerService.log_error("Failed to write JSON file for chunk_id: %s",chunk_id,exc=exc,)
            raise

        return file_path

    async def process_sentence(self, chunk: Chunk) -> tuple:
        LoggerService.log_info("Processing sentence for chunk_id: %s with text: '%s'",
            chunk.id,chunk.text[:100] + "..." if len(chunk.text) > 100 else chunk.text,)

        start_time = datetime.now()

        try:
            LoggerService.log_debug("Calling TTS service for chunk_id: %s",chunk.id,)

            audio_transcription: TTSTranscription = self.audio_service.generate(
                chunk.id,
                [chunk.text],
            )

            LoggerService.log_debug("TTS generated audio for chunk_id: %s at: %s",chunk.id,audio_transcription.audio_path,)

            LoggerService.log_debug("Calling word-level service for chunk_id: %s",chunk.id,)

            word_level: WordLevelTranscription = (
                self.word_level_service.generate_word_mapping(
                    audio_transcription.audio_path
                )
            )

            LoggerService.log_debug("Word-level mapping generated for chunk_id: %s with %s segments",chunk.id,len(word_level.segments) if word_level.segments else 0,)

            chunk_json_path = self.generate_chunk_id_json(
                word_level,
                chunk.id,
            )

            elapsed_time = (datetime.now() - start_time).total_seconds()

            LoggerService.log_info("Sentence processing completed for chunk_id: %s in %.2fs",chunk.id,elapsed_time,)

            return (
                audio_transcription.audio_path,
                chunk_json_path,
            )

        except Exception as exc:
            LoggerService.log_error("Error processing sentence for chunk_id: %s",chunk.id,exc=exc,)
            raise

    async def save_audio_on_bucket(
        self,
        audio_path: str,
        chunk_id: str,
    ) -> None:
        LoggerService.log_info("Uploading audio to bucket for chunk_id: %s from path: %s",chunk_id,audio_path,)

        try:
            metadata = "audio/mpeg"
            file_name = Path(audio_path).name
            key = f"audio/{chunk_id}/{file_name}"

            if audio_path.endswith(".wav"):
                metadata = "audio/wav"

            normalized_audio_path = f"./{audio_path.lstrip('./')}"

            LoggerService.log_debug("Audio upload details - Chunk ID: %s, Key: %s, Metadata: %s, File size: %s bytes",chunk_id,key,metadata,Path(normalized_audio_path).stat().st_size,)

            await self.bucket.upload(
                key,
                normalized_audio_path,
                metadata,
            )

            LoggerService.log_info("Audio successfully uploaded to bucket - Chunk ID: %s, Key: %s",chunk_id,key,)

            return key

        except Exception as exc:
            LoggerService.log_error("Failed to upload audio for chunk_id: %s",chunk_id,
                exc=exc,)
            raise

    async def save_json_on_bucket(
        self,
        json_path: str,
        chunk_id: str,
    ) -> None:
        LoggerService.log_info("Uploading JSON to bucket for chunk_id: %s from path: %s",
            chunk_id,json_path,)

        try:
            metadata = "application/json"
            file_name = Path(json_path).name
            key = f"chunks/{chunk_id}/{file_name}"

            LoggerService.log_debug("JSON upload details - Chunk ID: %s, Key: %s, File size: %s bytes",chunk_id,key,Path(json_path).stat().st_size,)

            await self.bucket.upload(
                key,
                json_path,
                metadata,
            )

            LoggerService.log_info("JSON successfully uploaded to bucket - Chunk ID: %s, Key: %s",chunk_id,key,)

            return key

        except Exception as exc:
            LoggerService.log_error("Failed to upload JSON for chunk_id: %s",chunk_id,exc=exc,)
            raise

    async def run(self):
        LoggerService.log_info("AudioWorker started and waiting for messages...")

        processed_count = 0
        error_count = 0

        while True:
            try:
                LoggerService.log_debug("Waiting for message from queue...")

                message = await self._queue.consume()

                if message is None:
                    LoggerService.log_debug("Received empty message, continuing...")
                    continue

                LoggerService.log_info("Received message: %s",message,)

                job_id = message.get("job_id")

                if not job_id:
                    LoggerService.log_warning("Message missing 'job_id', skipping: %s",message,)
                    continue

                worker_id: str = CommonData.get_worker_id()

                if not worker_id:
                    LoggerService.log_error("Unable to get worker_id, cannot process job")
                    continue

                LoggerService.log_info("Attempting to claim job_id: %s with worker_id: %s",job_id,worker_id,)

                job: Job = await self._jobs.claim(
                    worker_id,
                    job_id=job_id,
                )

                if job is None:
                    LoggerService.log_warning("Failed to claim job_id: %s - already claimed or doesn't exist",job_id,)
                    continue

                LoggerService.log_info("Job claimed successfully - Job ID: %s, Chunk ID: %s",job.id,job.chunk_id,)

                chunk: Chunk = await self.chunks.get_by_id(job.chunk_id)
                

                if not chunk:
                    LoggerService.log_error("Chunk not found - Job ID: %s, Chunk ID: %s",job_id,job.chunk_id,)

                    await self._jobs.fail(
                        job_id=job_id,
                        worker_id=worker_id,
                        error_code=404,
                        error_message=f"Chunk {job.chunk_id} not found",
                    )

                    continue

                LoggerService.log_info("Processing chunk_id: %s - Text length: %s chars",chunk.id,len(chunk.text),)

                try:
                    start_time = datetime.now()

                    audio_path, chunk_json_path = await self.process_sentence(chunk)

                    LoggerService.log_debug("Generated files for chunk_id: %s - Audio: %s, JSON: %s",chunk.id,audio_path,chunk_json_path,)

                    audio_path_bucket = await self.save_audio_on_bucket(
                        audio_path,
                        chunk.id,
                    )

                    json_path_bucket = await self.save_json_on_bucket(
                        chunk_json_path,
                        chunk.id,
                    )

                    audio_size = CommonData.file_size_from_path(audio_path)

                    json_size = CommonData.file_size_from_path(chunk_json_path)

                    LoggerService.log_debug("File sizes for chunk_id: %s - Audio: %s bytes, JSON: %s bytes",chunk.id,audio_size,json_size,)

                    # Create audio asset
                    audio_asset = AudioAsset(
                        id=uuid.uuid4(),
                        chunk_id=chunk.id,
                        storage_key=audio_path_bucket,
                        format="AUDIO",
                        size=audio_size,
                        status=BookStatus.COMPLETED,
                        created_at=datetime.now(),
                    )

                    await self.audio_asset.create(audio_asset)

                    LoggerService.log_debug("Audio asset created for chunk_id: %s - Storage key: %s",chunk.id,audio_path_bucket,)

                    # Create JSON asset
                    json_asset = MediaManifest(
                        id=uuid.uuid4(),
                        book_id=None,
                        chunk_id=chunk.id,
                        type="Content-Type: application/json",
                        storage_key=json_path_bucket,
                        status=BookStatus.COMPLETED,
                        created_at= datetime.now()
                    )

                    await self.media_manifest.create(json_asset)

                    LoggerService.log_debug("JSON asset created for chunk_id: %s - Storage key: %s",chunk.id,json_path_bucket,)

                    await self._jobs.complete(job.id)

                    await self.chunks.update_status(chunk.id,BookStatus.COMPLETED)

                    LoggerService.log_info("Job completed successfully - Job ID: %s, Chunk ID: %s",job.id,chunk.id,)

                    file_path_audio = Path(audio_path)
                    file_path_json = Path(chunk_json_path)

                    file_path_audio.unlink(missing_ok=True)
                    file_path_json.unlink(missing_ok=True)

                    LoggerService.log_debug("Cleaned up local files for chunk_id: %s",chunk.id,)

                    processed_count += 1

                    elapsed_time = (datetime.now() - start_time).total_seconds()

                    LoggerService.log_info("Total processing time for chunk_id: %s: %.2fs",chunk.id,elapsed_time,)

                except Exception as exc:
                    error_count += 1

                    LoggerService.log_error("Exception processing chunk_id: %s",chunk.id,
                        exc=exc,)

                    # Try to mark job as failed
                    try:
                        await self._jobs.fail(
                            job_id=job_id,
                            worker_id=worker_id,
                            error_code=500,
                            error_message=str(exc),
                        )

                        LoggerService.log_info("Job marked as failed - Job ID: %s",job_id,)

                    except Exception as fail_error:
                        LoggerService.log_error(
                            "Failed to mark job as failed - Job ID: %s",
                            job_id,
                            exc=fail_error,
                        )

            except Exception as exc:
                error_count += 1

                LoggerService.log_error("Unexpected error in AudioWorker main loop",
                    exc=exc,)

            finally:
                total_count = processed_count + error_count

                if total_count > 0 and total_count % 10 == 0:
                    LoggerService.log_info("AudioWorker stats - Processed: %s, Errors: %s, Total: %s",processed_count,error_count,total_count,)
