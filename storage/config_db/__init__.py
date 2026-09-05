"""Camada de acesso ao PostgreSQL (pool assíncrono via psycopg_pool)."""

from .config import DatabaseConfig
from .connection import create_pool
from .database import Database

__all__ = ["DatabaseConfig", "create_pool", "Database"]
