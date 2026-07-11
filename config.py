"""
config.py — Centralised application configuration.

All environment-specific settings live here.
Override any value by setting the corresponding environment variable.
Never hardcode secrets in source code — use .env for local dev.

Design: Uses a Config dataclass with class-level defaults.
        Environment variables always take precedence.
        A single get_config() call returns the active config object.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env file (only effective in local development; no-op in production)
load_dotenv()

# ── Project paths ──────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).resolve().parent
DATA_DIR        = BASE_DIR / "data"
RAW_DATA_PATH   = DATA_DIR / "raw"  / "tourism_dataset.csv"
CLEAN_DATA_PATH = DATA_DIR / "cleaned" / "tourism_cleaned.csv"
DB_PATH         = DATA_DIR / "cleaned" / "tourism.db"


@dataclass
class Config:
    """Base configuration — values shared across all environments."""

    # ── Application ───────────────────────────────────────────────────────
    APP_TITLE: str        = "Tourism Analytics"
    APP_VERSION: str      = "1.0.0"
    DEBUG: bool           = os.getenv("DEBUG", "false").lower() == "true"

    # ── Server ────────────────────────────────────────────────────────────
    HOST: str             = os.getenv("HOST", "0.0.0.0")
    PORT: int             = int(os.getenv("PORT", "8050"))

    # ── Database ──────────────────────────────────────────────────────────
    # SQLite by default (zero-config). Switch to PostgreSQL by setting:
    #   DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
    DATABASE_URL: str     = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DB_PATH}"
    )

    # ── Caching ───────────────────────────────────────────────────────────
    CACHE_TYPE: str       = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_TIMEOUT: int    = int(os.getenv("CACHE_TIMEOUT", "600"))   # 10 min

    # ── UI Defaults ───────────────────────────────────────────────────────
    DEFAULT_THEME: str    = os.getenv("DEFAULT_THEME", "dark")
    DEFAULT_PAGE_SIZE: int = 20

    # ── Data ──────────────────────────────────────────────────────────────
    CLEAN_DATA_PATH: Path = CLEAN_DATA_PATH
    DB_PATH: Path         = DB_PATH

    # ── Chart Defaults ────────────────────────────────────────────────────
    CHART_HEIGHT_SM: int  = 320
    CHART_HEIGHT_MD: int  = 420
    CHART_HEIGHT_LG: int  = 520

    # ── Forecast ──────────────────────────────────────────────────────────
    FORECAST_PERIODS: int = 12     # Months ahead to forecast
    MOVING_AVG_WINDOW: int = 3     # Rolling average window in months


# Singleton pattern: one config object for the entire app lifetime
_config: Config | None = None


def get_config() -> Config:
    """Return the application configuration singleton."""
    global _config
    if _config is None:
        _config = Config()
    return _config


# Convenience export — most modules just do: from config import config
config = get_config()
