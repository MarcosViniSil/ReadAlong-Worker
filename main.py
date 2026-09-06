import asyncio

from jobs_queue.config import QueueConfig
from jobs_queue.queue import AudioQueue
from audioWorker import AudioWorker
from storage.audioAssetRepository.impl.audioAssetRepositoryImpl import (
    AudioAssetRepositoryImpl,
)
from storage.bucket.config import load_bucket_config
from storage.bucket.impl.bucketProviderImpl import BucketProviderImpl
from storage.chunkRepository.impl.ChunkRepositoryImpl import ChunkRepositoryImpl
from storage.config_db.connection import DatabaseConfig
from storage.config_db.database import Database
from storage.mediaManifestRepository.impl.mediaManifestRepositoryImpl import MediaManifestRepositoryRepositoryImpl
from tts.imp.TTSProviderImpl import KokoroProviderImpl
from storage.JobRepository.impl.jobRepositoryImpl import (
    JobRepositoryImpl,
)
from word_level.impl.word_level_impl import WordLevelImpl


async def main():

    db_config = DatabaseConfig()
    queue_config = QueueConfig()

    db = Database(db_config)
    queue = AudioQueue(queue_config)

    stop_event = asyncio.Event()

    jobs = JobRepositoryImpl(db)
    chunks = ChunkRepositoryImpl(db)
    audio_asset = AudioAssetRepositoryImpl(db)
    media_manifest = MediaManifestRepositoryRepositoryImpl(db)

    audio_service = KokoroProviderImpl()
    word_level = WordLevelImpl()

    bucket_settings = load_bucket_config()
    bucket = BucketProviderImpl(bucket_settings)

    await db.open()

    try:

        await queue.ping()

        worker = AudioWorker(
            queue=queue,
            jobs=jobs,
            chunks=chunks,
            audio_service=audio_service,
            word_level_service=word_level,
            bucket=bucket,
            audio_asset=audio_asset,
            media_manifest=media_manifest
        )

        await worker.run()

        await asyncio.gather(
            db.run_health_loop(
                stop_event=stop_event,
            ),
            # run_worker_heartbeat(
            #    db=db,
            #    worker_id=worker_id,
            #    stop_event=stop_event,
            # ),
        )

    finally:

        await queue.close()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
