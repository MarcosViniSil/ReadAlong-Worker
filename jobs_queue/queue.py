from __future__ import annotations

import json
import logging

import redis.asyncio as redis

from log.loggerService import LoggerService

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

        LoggerService.log_info("Message received in the queue: %s", result)

        if result is None:
            return None

        _, raw_message = result

        try:
            return json.loads(raw_message)

        except json.JSONDecodeError:
            LoggerService.log_exception(
                "Invalid message received: %s",
                raw_message,
            )

            return None
