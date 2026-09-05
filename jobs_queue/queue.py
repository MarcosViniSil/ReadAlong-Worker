from __future__ import annotations

import json
import logging

import redis.asyncio as redis

from .config import QueueConfig
from .connection import create_redis_client

logger = logging.getLogger(__name__)


class AudioQueue:

    def __init__(
        self,
        config: QueueConfig,
    ) -> None:

        self._config = config

        self._redis = create_redis_client(config)

    async def close(self) -> None:
        await self._redis.aclose()

    async def ping(self) -> bool:

        return await self._redis.ping()

    async def consume(
        self,
    ) -> dict | None:

        result = await self._redis.blpop(
            self._config.jobs_key,
            timeout=self._config.queue_block_timeout,
        )

        if result is None:
            return None

        _, raw_message = result

        try:
            return json.loads(raw_message)

        except json.JSONDecodeError:
            logger.exception(
                "Mensagem inválida recebida da fila: %s",
                raw_message,
            )

            return None
