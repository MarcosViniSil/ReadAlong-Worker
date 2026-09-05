from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if value in (None, ""):
        return default

    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class QueueConfig:
    host: str = field(
        default_factory=lambda: os.getenv(
            "REDIS_HOST",
            "localhost",
        )
    )

    port: int = field(
        default_factory=lambda: _get_int(
            "REDIS_PORT",
            6379,
        )
    )

    db: int = field(
        default_factory=lambda: _get_int(
            "REDIS_DB",
            0,
        )
    )

    password: str | None = field(
        default_factory=lambda: (os.getenv("REDIS_PASSWORD") or None)
    )

    jobs_key: str = field(
        default_factory=lambda: os.getenv(
            "REDIS_JOBS_KEY",
            "readalong:audio:jobs",
        )
    )

    connect_timeout: float = field(
        default_factory=lambda: float(
            os.getenv(
                "REDIS_CONNECT_TIMEOUT",
                "5",
            )
        )
    )

    socket_timeout: float = field(
        default_factory=lambda: float(
            os.getenv(
                "REDIS_SOCKET_TIMEOUT",
                "10",
            )
        )
    )

    health_check_interval: int = field(
        default_factory=lambda: _get_int(
            "REDIS_HEALTH_CHECK_INTERVAL",
            30,
        )
    )

    queue_block_timeout: int = field(
        default_factory=lambda: _get_int(
            "REDIS_QUEUE_BLOCK_TIMEOUT",
            5,
        )
    )
