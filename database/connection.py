"""
database/connection.py — SQLAlchemy engine and session factory.

Design decision — why SQLAlchemy over raw sqlite3?
  • Same code works with SQLite (dev) AND PostgreSQL (prod).
    Switching requires only a DATABASE_URL environment variable change.
  • Connection pooling is handled automatically.
  • Type-safe query building is possible via ORM (optional).
  • Thread-safe session management via scoped_session.

The engine is created once at module import time (singleton pattern).
All query functions call get_session() to get a fresh session.
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import config

log = logging.getLogger(__name__)

# ── Engine ─────────────────────────────────────────────────────────────────
# connect_args only needed for SQLite (disables same-thread check for Dash)
_connect_args = {}
if config.DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(
    config.DATABASE_URL,
    connect_args=_connect_args,
    echo=False,           # Set True to see raw SQL in console (debug only)
    pool_pre_ping=True,   # Reconnect on stale connections (production safety)
)

# ── Session Factory ─────────────────────────────────────────────────────────
_SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager that provides a database session.

    Usage:
        with get_session() as session:
            result = session.execute(text("SELECT ...")).fetchall()

    The session is automatically committed on success or rolled back on error.
    Always closes the session on exit to return the connection to the pool.
    """
    session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception as exc:
        session.rollback()
        log.error(f"DB session error: {exc}", exc_info=True)
        raise
    finally:
        session.close()


# ── SQLite WAL mode (performance) ──────────────────────────────────────────
# WAL (Write-Ahead Logging) makes SQLite faster for concurrent reads.
# This is only applied for SQLite; PostgreSQL ignores it.
if config.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")   # 64 MB cache
        cursor.close()


# ── Base Model ─────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """All SQLAlchemy ORM models inherit from this base."""
    pass
