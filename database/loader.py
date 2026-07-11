"""
database/loader.py — Load the cleaned CSV into SQLite (one-time setup).

Run this once before starting the app for the first time:
    python -m database.loader

Or it is called automatically at app startup if the DB is missing.

Design: Uses pandas.DataFrame.to_sql() which:
  • Creates the table schema from the DataFrame dtypes
  • Handles batch inserts efficiently (chunksize=5000)
  • if_exists="replace" makes this idempotent (safe to re-run)
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import inspect, text

from config import config
from database.connection import engine

log = logging.getLogger(__name__)

TABLE_NAME = "tourism"


def _table_exists() -> bool:
    """Return True if the tourism table exists and has rows."""
    inspector = inspect(engine)
    if TABLE_NAME not in inspector.get_table_names():
        return False
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}"))
        return result.scalar() > 0


def load_data_to_db(
    csv_path: Path = config.CLEAN_DATA_PATH,
    force_reload: bool = False,
) -> int:
    """
    Load the cleaned CSV into the SQLite database.

    Parameters
    ----------
    csv_path     : Path to the cleaned CSV file
    force_reload : If True, drops the existing table and reloads from scratch

    Returns
    -------
    int — number of rows loaded, or 0 if skipped (already loaded)

    Raises
    ------
    FileNotFoundError — if csv_path does not exist
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at: {csv_path}\n"
            f"Run the data cleaning pipeline first:\n"
            f"  cd ../tourism-trends-analysis && python src/data_cleaner.py"
        )

    # Skip if already loaded (and not forcing a reload)
    if _table_exists() and not force_reload:
        log.info("Database already populated. Pass force_reload=True to reload.")
        return 0

    log.info(f"Loading data from {csv_path} …")
    df = pd.read_csv(csv_path, low_memory=False)

    # Store Date as ISO string (SQLite has no native DATE type)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Cast numeric columns cleanly — coerce errors to 0
    int_cols   = ["Visitors", "Repeat_Visitor", "Year", "Month", "Quarter"]
    float_cols = ["Revenue_USD", "Average_Stay_Days", "Hotel_Occupancy", "Customer_Rating"]

    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    rows = len(df)
    log.info(f"  Writing {rows:,} rows to SQLite table '{TABLE_NAME}' …")

    # Write to SQLite — if_exists="replace" is idempotent
    # NOTE: Do NOT use method="multi" with SQLite — it generates a single
    # INSERT with all row values as bind parameters, exceeding SQLite's
    # SQLITE_MAX_VARIABLE_NUMBER limit (999). Default method is safe.
    df.to_sql(
        TABLE_NAME,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=5000,
    )

    # Create indexes on commonly filtered columns (large query speedup)
    index_definitions = [
        f"CREATE INDEX IF NOT EXISTS idx_year    ON {TABLE_NAME}(Year)",
        f"CREATE INDEX IF NOT EXISTS idx_month   ON {TABLE_NAME}(Month)",
        f"CREATE INDEX IF NOT EXISTS idx_country ON {TABLE_NAME}(Country)",
        f"CREATE INDEX IF NOT EXISTS idx_city    ON {TABLE_NAME}(City)",
        f"CREATE INDEX IF NOT EXISTS idx_type    ON {TABLE_NAME}(Tourist_Type)",
        f"CREATE INDEX IF NOT EXISTS idx_season  ON {TABLE_NAME}(Season)",
        f"CREATE INDEX IF NOT EXISTS idx_date    ON {TABLE_NAME}(Date)",
    ]

    with engine.connect() as conn:
        for idx_sql in index_definitions:
            conn.execute(text(idx_sql))
        conn.commit()

    log.info(f"  Done! {rows:,} rows + {len(index_definitions)} indexes created.")
    return rows


def get_filter_options() -> dict:
    """
    Return unique values for all filterable columns.
    Called once at app startup to populate dropdown options.

    Returns
    -------
    dict with keys: countries, cities, tourist_types, seasons, years
    """
    queries = {
        "countries":     f"SELECT DISTINCT Country      FROM {TABLE_NAME} ORDER BY Country",
        "cities":        f"SELECT DISTINCT City         FROM {TABLE_NAME} ORDER BY City",
        "tourist_types": f"SELECT DISTINCT Tourist_Type FROM {TABLE_NAME} ORDER BY Tourist_Type",
        "seasons":       f"SELECT DISTINCT Season       FROM {TABLE_NAME} ORDER BY Season",
        "years":         f"SELECT DISTINCT Year         FROM {TABLE_NAME} ORDER BY Year",
    }

    options: dict = {}
    with engine.connect() as conn:
        for key, query in queries.items():
            result = conn.execute(text(query)).fetchall()
            options[key] = [row[0] for row in result if row[0] is not None]

    return options


if __name__ == "__main__":
    """Allow running directly: python -m database.loader"""
    import logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    loaded = load_data_to_db(force_reload=True)
    print(f"Loaded {loaded:,} rows.")
