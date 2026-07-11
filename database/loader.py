"""
database/loader.py — Load the cleaned CSV into SQLite (one-time setup).

Run this once before starting the app for the first time:
    python -c "from database.loader import load_data_to_db; load_data_to_db()"

Or it is called automatically by app.py on first startup if the DB is missing.

Design: Uses pandas.DataFrame.to_sql() which:
  • Creates the table schema from the DataFrame dtypes
  • Handles batch inserts efficiently (chunksize=5000)
  • If the table exists and if_exists="replace": drops and recreates
    (idempotent — safe to run multiple times)
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from config import config
from database.connection import engine

log = logging.getLogger(__name__)

TABLE_NAME = "tourism"


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
    int — number of rows loaded

    Raises
    ------
    FileNotFoundError — if csv_path does not exist
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Cleaned dataset not found at {csv_path}.\n"
            f"Run the data cleaning pipeline first:\n"
            f"  cd ../tourism-trends-analysis && python src/data_cleaner.py"
        )

    # Check if table already exists and skip if not force_reload
    from sqlalchemy import inspect
    inspector = inspect(engine)
    if TABLE_NAME in inspector.get_table_names() and not force_reload:
        with engine.connect() as conn:
            count = conn.execute(
                pd.io.sql.pandasSQL_builder(conn).execute(
                    f"SELECT COUNT(*) FROM {TABLE_NAME}"
                )
            )
        log.info(f"Database already loaded. Use force_reload=True to reload.")
        return 0

    log.info(f"Loading data from {csv_path} …")
    df = pd.read_csv(csv_path, low_memory=False)

    # Ensure Date is stored as string (SQLite has no native DATE type)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")

    # Cast numeric columns cleanly
    df["Visitors"]          = pd.to_numeric(df["Visitors"],          errors="coerce").fillna(0).astype(int)
    df["Revenue_USD"]       = pd.to_numeric(df["Revenue_USD"],       errors="coerce").fillna(0.0)
    df["Average_Stay_Days"] = pd.to_numeric(df["Average_Stay_Days"], errors="coerce").fillna(0.0)
    df["Hotel_Occupancy"]   = pd.to_numeric(df["Hotel_Occupancy"],   errors="coerce").fillna(0.0)
    df["Customer_Rating"]   = pd.to_numeric(df["Customer_Rating"],   errors="coerce").fillna(0.0)
    df["Repeat_Visitor"]    = pd.to_numeric(df["Repeat_Visitor"],    errors="coerce").fillna(0).astype(int)
    df["Year"]              = pd.to_numeric(df["Year"],              errors="coerce").fillna(0).astype(int)
    df["Month"]             = pd.to_numeric(df["Month"],             errors="coerce").fillna(0).astype(int)
    df["Quarter"]           = pd.to_numeric(df["Quarter"],           errors="coerce").fillna(0).astype(int)

    rows = len(df)
    log.info(f"  Writing {rows:,} rows to SQLite table '{TABLE_NAME}' …")

    # Write to SQLite — if_exists="replace" makes this idempotent
    df.to_sql(
        TABLE_NAME,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=5000,      # Write in batches of 5,000 rows
        method="multi",      # Faster batch insert
    )

    # Create indexes for common filter columns (massive query speedup)
    with engine.connect() as conn:
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_year    ON {TABLE_NAME}(Year)",
            f"CREATE INDEX IF NOT EXISTS idx_month   ON {TABLE_NAME}(Month)",
            f"CREATE INDEX IF NOT EXISTS idx_country ON {TABLE_NAME}(Country)",
            f"CREATE INDEX IF NOT EXISTS idx_city    ON {TABLE_NAME}(City)",
            f"CREATE INDEX IF NOT EXISTS idx_type    ON {TABLE_NAME}(Tourist_Type)",
            f"CREATE INDEX IF NOT EXISTS idx_season  ON {TABLE_NAME}(Season)",
            f"CREATE INDEX IF NOT EXISTS idx_date    ON {TABLE_NAME}(Date)",
        ]
        for idx_sql in indexes:
            conn.execute(pd.io.sql.pandasSQL_builder(conn).execute.__class__(idx_sql) if False else __import__('sqlalchemy').text(idx_sql))
        conn.commit()

    log.info(f"  Done! {rows:,} rows + 7 indexes created.")
    return rows


def get_filter_options() -> dict:
    """
    Return unique values for all filterable columns.
    Called once at app startup to populate dropdown options.

    Returns
    -------
    dict with keys: countries, cities, tourist_types, seasons, years
    """
    from sqlalchemy import text as sql_text

    options = {}
    queries = {
        "countries"    : f"SELECT DISTINCT Country     FROM {TABLE_NAME} ORDER BY Country",
        "cities"       : f"SELECT DISTINCT City        FROM {TABLE_NAME} ORDER BY City",
        "tourist_types": f"SELECT DISTINCT Tourist_Type FROM {TABLE_NAME} ORDER BY Tourist_Type",
        "seasons"      : f"SELECT DISTINCT Season      FROM {TABLE_NAME} ORDER BY Season",
        "years"        : f"SELECT DISTINCT Year        FROM {TABLE_NAME} ORDER BY Year",
    }

    with engine.connect() as conn:
        for key, query in queries.items():
            result = conn.execute(sql_text(query)).fetchall()
            options[key] = [row[0] for row in result if row[0] is not None]

    return options
