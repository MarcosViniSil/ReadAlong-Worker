import asyncio

from storage.config_db.config import DatabaseConfig
from storage.config_db.database import Database


async def main():

    config = DatabaseConfig()

    db = Database(config)

    await db.open()

    stop_event = asyncio.Event()

    try:

        await asyncio.gather(
            # run_worker(
            #    db=db,
            #    stop_event=stop_event,
            # ),
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

        stop_event.set()

        await db.close()
