"""Criação do pool de conexões assíncrono (psycopg_pool)."""

from __future__ import annotations

import logging

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from .config import DatabaseConfig

logger = logging.getLogger(__name__)


async def _sanity_check(conn: AsyncConnection) -> None:
    cur = await conn.execute("SELECT 1")
    await cur.fetchone()


def _connection_kwargs(cfg: DatabaseConfig) -> dict:
    return {
        "connect_timeout": cfg.connect_timeout,
        "keepalives": 1,
        "keepalives_idle": cfg.tcp_keepalive_idle,
        "keepalives_interval": cfg.tcp_keepalive_interval,
        "keepalives_count": cfg.tcp_keepalive_count,
        "application_name": "readalong-worker",
    }


def create_pool(cfg: DatabaseConfig) -> AsyncConnectionPool:
    return AsyncConnectionPool(
        cfg.db_url,
        kwargs=_connection_kwargs(cfg),
        min_size=cfg.pool_min_size,
        max_size=cfg.pool_max_size,
        max_lifetime=cfg.pool_max_lifetime,
        reconnect_timeout=cfg.reconnect_timeout,
        timeout=cfg.acquire_timeout,
        check=_sanity_check,
        open=False,
        name="readalong-worker",
    )
