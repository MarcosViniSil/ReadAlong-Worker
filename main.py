import asyncio
import logging
import uuid

from jobs_queue.config import QueueConfig
from jobs_queue.queue import AudioQueue

from audioWorker import AudioWorker
from storage.config_db.connection import DatabaseConfig
from storage.config_db.database import Database

from storage.JobRepository.impl.jobRepositoryImpl import (
    JobRepositoryImpl,
)

logger = logging.getLogger(__name__)


async def main():

    db_config = DatabaseConfig()
    queue_config = QueueConfig()

    db = Database(db_config)
    queue = AudioQueue(queue_config)


    jobs = JobRepositoryImpl(db)

    await db.open()

    try:

        await queue.ping()

        logger.info("Redis conectado")

        logger.info("PostgreSQL conectado")

        worker = AudioWorker(
            queue=queue,
            jobs=jobs,
        )

        await worker.run()

    finally:

        await queue.close()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
