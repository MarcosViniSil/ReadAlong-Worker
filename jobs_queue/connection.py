from __future__ import annotations

import redis.asyncio as redis

from .config import QueueConfig


def create_redis_client(
    config: QueueConfig,
) -> redis.Redis:

    return redis.Redis(
        host=config.host,
        port=config.port,
        db=config.db,
        password=config.password,
        decode_responses=True,
        socket_connect_timeout=config.connect_timeout,
        socket_timeout=config.socket_timeout,
        health_check_interval=config.health_check_interval,
    )
