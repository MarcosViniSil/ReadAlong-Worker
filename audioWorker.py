import json
import time
from dataclasses import asdict
import uuid
from jobs_queue.queue import AudioQueue
from models.Job import Job
from models.TTSTranscription import TTSTranscription
from models.chunk import Chunk
from models.chunk_audio import ChunkAudio, ChunkWord
from models.wordLevelTranscription import WordLevelTranscription
from storage.JobRepository.jobRepositoryProvider import JobRepositoryProvider
from storage.chunkRepository.chunkRepositoryProvider import ChunkRepositoryProvider
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
    ):
        self._queue = queue
        self._jobs = jobs
        self.chunks = chunks
        self.audio_service = audio_service
        self.word_level_service = word_level_service

    def generate_chunk_id_json(
        self,
        word_level: WordLevelTranscription,
        chunk_id: str
    ) -> None:

        if not word_level.segments:
            raise ValueError("none segment found")

        first_segment = word_level.segments[0]
        last_segment = word_level.segments[-1]

        chunk_audio = ChunkAudio(
            start=float(first_segment["start"]),
            end=float(last_segment["end"]),
            words=[],
        )

        for segment in word_level.segments:

            for word in segment["words"]:

                chunk_audio.words.append(
                    ChunkWord(
                        text=word["word"],
                        start=float(word["start"]),
                        end=float(word["end"]),
                    )
                )

        file_path = f"{chunk_id}.json"

        with open(file_path,"w",encoding="utf-8",) as file:
            json.dump(asdict(chunk_audio),file,ensure_ascii=False,indent=2,)


    async def process_sentence(self, chunk: Chunk) -> None:
        audioTranscription: TTSTranscription = self.audio_service.generate(
            chunk.id, [chunk.text]
        )

        wordLevel: WordLevelTranscription = (
            self.word_level_service.generate_word_mapping(
                audioTranscription.audio_path, chunk.id
            )
        )

        self.generate_chunk_id_json(wordLevel,chunk.id)

    async def run(self):

        while True:

            message = await self._queue.consume()

            if message is None:
                continue

            print("message ", message)

            job_id = message.get("job_id")

            if not job_id:
                continue

            job: Job = await self._jobs.claim(
                job_id=job_id,
            )

            if job is None:

                # Outro worker já adquiriu o job
                # ou ele não está mais pending.
                continue

            chunk: Chunk = await self.chunks.get_by_id(job.chunk_id)
            print("chunk ", chunk)

            try:

                await self.process_sentence(chunk)
                print("message ", message)
                print("job_id ", job_id)
                print("job ", job)
                time.sleep(10)

            except Exception as exc:
                pass

                # await self._jobs.fail(
                #    job_id=job_id,
                #    worker_id=self._worker_id,
                #    error_code=500,
                #    error_message=str(exc),
                # )

            else:
                pass

                # await self._jobs.complete(
                #    job_id=job_id,
                #    worker_id=self._worker_id,
                # )
