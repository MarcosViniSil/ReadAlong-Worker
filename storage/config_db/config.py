from __future__ import annotations

import os
from dataclasses import dataclass, field


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value in (None, ""):
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class DatabaseConfig:
    db_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", "postgresql://localhost:5432/readalong"
        )
    )
    pool_min_size: int = field(default_factory=lambda: _get_int("DB_POOL_MIN_SIZE", 2))
    pool_max_size: int = field(default_factory=lambda: _get_int("DB_POOL_MAX_SIZE", 10))

    pool_max_lifetime: int | None = field(
        default_factory=lambda: (
            None
            if os.getenv("DB_POOL_MAX_LIFETIME", "") == ""
            else _get_int("DB_POOL_MAX_LIFETIME", 1800)
        )
    )
    acquire_timeout: int = field(
        default_factory=lambda: _get_int("DB_ACQUIRE_TIMEOUT", 30)
    )
    connect_timeout: int = field(
        default_factory=lambda: _get_int("DB_CONNECT_TIMEOUT", 10)
    )
    reconnect_timeout: int = field(
        default_factory=lambda: _get_int("DB_RECONNECT_TIMEOUT", 300)
    )
    tcp_keepalive_idle: int = field(
        default_factory=lambda: _get_int("DB_KEEPALIVE_IDLE", 60)
    )
    tcp_keepalive_interval: int = field(
        default_factory=lambda: _get_int("DB_KEEPALIVE_INTERVAL", 15)
    )
    tcp_keepalive_count: int = field(
        default_factory=lambda: _get_int("DB_KEEPALIVE_COUNT", 6)
    )
    heartbeat_interval: int = field(
        default_factory=lambda: _get_int("DB_HEARTBEAT_INTERVAL", 15)
    )
