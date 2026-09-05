from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncIterator

from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from .config import DatabaseConfig
from .connection import create_pool

logger = logging.getLogger(__name__)


class Database:

    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._pool = create_pool(config)

    @property
    def pool(self) -> AsyncConnectionPool:
        return self._pool

    async def open(self) -> None:
        await self._pool.open()

    async def close(self) -> None:
        if not self._pool.closed:
            await self._pool.close()

    @asynccontextmanager
    async def connection(self):
        async with self._pool.connection(timeout=self._config.acquire_timeout) as conn:
            conn.row_factory = dict_row
            yield conn

    @asynccontextmanager
    async def transaction(self):
        async with self._pool.connection(timeout=self._config.acquire_timeout) as conn:
            conn.row_factory = dict_row

            async with conn.transaction():
                yield conn

    async def check(self) -> list[int]:
        return await self._pool.check()

    async def run_health_loop(
        self,
        stop_event: asyncio.Event,
    ) -> None:

        interval = self._config.heartbeat_interval

        while not stop_event.is_set():

            try:
                broken = await self._pool.check()

                if broken:
                    logger.warning(
                        "conexões quebradas recicladas: %s",
                        broken,
                    )

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception("erro verificando pool do PostgreSQL")

            try:
                await asyncio.wait_for(
                    stop_event.wait(),
                    timeout=interval,
                )

            except asyncio.TimeoutError:
                pass
