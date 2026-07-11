"""
services/data_service.py — Centralized data access layer.

ALL data queries go through this module. Features:
  • Single source of truth for all analytics queries
  • Flask-Caching integration (cache_timeout=600s)
  • Filter application (year, country, tourist_type, season)
  • Returns pandas DataFrames — pages do their own Plotly rendering
  • Graceful empty-DataFrame returns on missing data

Dataset columns (49,468 rows, 2020-2025):
  Tourist_ID, Date, Year, Month, Quarter, Country, City, Tourist_Type,
  Visitors, Revenue_USD, Average_Stay_Days, Hotel_Occupancy, Season,
  Transport_Mode, Accommodation_Type, Travel_Purpose, Booking_Channel,
  Weather, Customer_Rating, Repeat_Visitor
"""
from __future__ import annotations
import logging
from functools import lru_cache
import pandas as pd
import numpy as np
from sqlalchemy import text
from database.connection import engine

log = logging.getLogger(__name__)

# ── Module-level DataFrame cache (loaded once at startup) ──────────────────
_df: pd.DataFrame | None = None


def get_df() -> pd.DataFrame:
    """Return the full DataFrame, loading from SQLite once."""
    global _df
    if _df is None:
        log.info("Loading tourism data into memory…")
        _df = pd.read_sql("SELECT * FROM tourism", engine)
        _df["Date"] = pd.to_datetime(_df["Date"], errors="coerce")
        _df["Revenue_USD"] = pd.to_numeric(_df["Revenue_USD"], errors="coerce").fillna(0)
        _df["Visitors"] = pd.to_numeric(_df["Visitors"], errors="coerce").fillna(0).astype(int)
        log.info(f"  Loaded {len(_df):,} rows.")
    return _df


def apply_filters(
    df: pd.DataFrame,
    years: list | None = None,
    countries: list | None = None,
    tourist_types: list | None = None,
    seasons: list | None = None,
    quarters: list | None = None,
) -> pd.DataFrame:
    """Apply standard filters to a DataFrame slice."""
    if years:
        df = df[df["Year"].isin(years)]
    if countries:
        df = df[df["Country"].isin(countries)]
    if tourist_types:
        df = df[df["Tourist_Type"].isin(tourist_types)]
    if seasons:
        df = df[df["Season"].isin(seasons)]
    if quarters:
        df = df[df["Quarter"].isin(quarters)]
    return df


# ── Filter Option Lists ────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def get_filter_options() -> dict:
    df = get_df()
    return {
        "years":         sorted(df["Year"].unique().tolist()),
        "countries":     sorted(df["Country"].unique().tolist()),
        "cities":        sorted(df["City"].unique().tolist()),
        "tourist_types": sorted(df["Tourist_Type"].unique().tolist()),
        "seasons":       sorted(df["Season"].unique().tolist()),
        "quarters":      sorted(df["Quarter"].unique().tolist()),
        "transport":     sorted(df["Transport_Mode"].unique().tolist()),
        "accommodation": sorted(df["Accommodation_Type"].unique().tolist()),
        "purposes":      sorted(df["Travel_Purpose"].unique().tolist()),
        "channels":      sorted(df["Booking_Channel"].unique().tolist()),
        "weather":       sorted(df["Weather"].unique().tolist()),
    }


# ══════════════════════════════════════════════════════════════════════════
# EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════════════════════════════════

def get_kpi_summary(filters: dict | None = None) -> dict:
    """Top-level KPIs for the Executive Overview page."""
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    if df.empty:
        return {}

    total_visitors = int(df["Visitors"].sum())
    total_revenue  = float(df["Revenue_USD"].sum())
    avg_stay       = float(df["Average_Stay_Days"].mean())
    avg_rating     = float(df["Customer_Rating"].mean())
    avg_occupancy  = float(df["Hotel_Occupancy"].mean())
    repeat_pct     = float(df["Repeat_Visitor"].mean() * 100)
    top_country    = df.groupby("Country")["Visitors"].sum().idxmax()
    top_city       = df.groupby("City")["Visitors"].sum().idxmax()
    avg_spend      = total_revenue / total_visitors if total_visitors else 0

    # YoY growth (latest year vs previous)
    years = sorted(df["Year"].unique())
    yoy_growth = None
    if len(years) >= 2:
        curr = df[df["Year"] == years[-1]]["Visitors"].sum()
        prev = df[df["Year"] == years[-2]]["Visitors"].sum()
        yoy_growth = ((curr - prev) / prev * 100) if prev else 0

    return {
        "total_visitors": total_visitors,
        "total_revenue":  total_revenue,
        "avg_stay":       round(avg_stay, 1),
        "avg_rating":     round(avg_rating, 2),
        "avg_occupancy":  round(avg_occupancy, 1),
        "repeat_pct":     round(repeat_pct, 1),
        "top_country":    top_country,
        "top_city":       top_city,
        "avg_spend":      round(avg_spend, 2),
        "yoy_growth":     round(yoy_growth, 1) if yoy_growth is not None else 0,
        "total_records":  len(df),
    }


def get_monthly_visitors(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby(["Year", "Month"])
        .agg(Visitors=("Visitors", "sum"), Revenue=("Revenue_USD", "sum"))
        .reset_index()
        .sort_values(["Year", "Month"])
    )


def get_yearly_summary(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    agg = df.groupby("Year").agg(
        Visitors=("Visitors", "sum"),
        Revenue=("Revenue_USD", "sum"),
        AvgStay=("Average_Stay_Days", "mean"),
        AvgRating=("Customer_Rating", "mean"),
        AvgOccupancy=("Hotel_Occupancy", "mean"),
    ).reset_index()
    agg["GrowthPct"] = agg["Visitors"].pct_change() * 100
    return agg


# ══════════════════════════════════════════════════════════════════════════
# TOURISM TRENDS
# ══════════════════════════════════════════════════════════════════════════

def get_seasonal_trends(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby(["Year", "Season"])
        .agg(Visitors=("Visitors", "sum"), Revenue=("Revenue_USD", "sum"))
        .reset_index()
    )


def get_quarterly_trends(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby(["Year", "Quarter"])
        .agg(Visitors=("Visitors", "sum"), Revenue=("Revenue_USD", "sum"))
        .reset_index()
    )


def get_type_trends(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby(["Year", "Tourist_Type"])
        .agg(Visitors=("Visitors", "sum"), Revenue=("Revenue_USD", "sum"))
        .reset_index()
    )


def get_moving_average(window: int = 3, filters: dict | None = None) -> pd.DataFrame:
    df = get_monthly_visitors(filters)
    df = df.groupby(["Year", "Month"])["Visitors"].sum().reset_index().sort_values(["Year", "Month"])
    df["MA"] = df["Visitors"].rolling(window=window, min_periods=1).mean()
    return df


# ══════════════════════════════════════════════════════════════════════════
# GEOGRAPHIC ANALYSIS
# ══════════════════════════════════════════════════════════════════════════

def get_country_stats(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby("Country")
        .agg(
            Visitors=("Visitors", "sum"),
            Revenue=("Revenue_USD", "sum"),
            AvgStay=("Average_Stay_Days", "mean"),
            AvgRating=("Customer_Rating", "mean"),
            AvgOccupancy=("Hotel_Occupancy", "mean"),
            Records=("Tourist_ID", "count"),
        )
        .reset_index()
        .sort_values("Visitors", ascending=False)
    )


def get_city_stats(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby(["City", "Country"])
        .agg(
            Visitors=("Visitors", "sum"),
            Revenue=("Revenue_USD", "sum"),
            AvgStay=("Average_Stay_Days", "mean"),
            AvgRating=("Customer_Rating", "mean"),
        )
        .reset_index()
        .sort_values("Visitors", ascending=False)
    )


def get_country_monthly(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby(["Country", "Year", "Month"])
        .agg(Visitors=("Visitors", "sum"), Revenue=("Revenue_USD", "sum"))
        .reset_index()
    )


# ══════════════════════════════════════════════════════════════════════════
# REVENUE ANALYTICS
# ══════════════════════════════════════════════════════════════════════════

def get_revenue_by_country(filters: dict | None = None) -> pd.DataFrame:
    return get_country_stats(filters)[["Country", "Revenue", "Visitors"]].head(20)


def get_revenue_by_type(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby("Tourist_Type")
        .agg(Revenue=("Revenue_USD", "sum"), Visitors=("Visitors", "sum"))
        .reset_index()
        .assign(AvgSpend=lambda x: x["Revenue"] / x["Visitors"])
    )


def get_revenue_by_channel(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby("Booking_Channel")
        .agg(Revenue=("Revenue_USD", "sum"), Visitors=("Visitors", "sum"))
        .reset_index()
    )


def get_revenue_by_accommodation(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby("Accommodation_Type")
        .agg(Revenue=("Revenue_USD", "sum"), Visitors=("Visitors", "sum"))
        .reset_index()
        .assign(AvgSpend=lambda x: x["Revenue"] / x["Visitors"])
    )


def get_monthly_revenue(filters: dict | None = None) -> pd.DataFrame:
    return get_monthly_visitors(filters)


# ══════════════════════════════════════════════════════════════════════════
# VISITOR BEHAVIOR
# ══════════════════════════════════════════════════════════════════════════

def get_by_purpose(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby("Travel_Purpose")
        .agg(Visitors=("Visitors", "sum"), Revenue=("Revenue_USD", "sum"),
             AvgStay=("Average_Stay_Days", "mean"))
        .reset_index()
        .sort_values("Visitors", ascending=False)
    )


def get_by_transport(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby("Transport_Mode")
        .agg(Visitors=("Visitors", "sum"), Revenue=("Revenue_USD", "sum"),
             AvgStay=("Average_Stay_Days", "mean"))
        .reset_index()
    )


def get_by_accommodation(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby("Accommodation_Type")
        .agg(Visitors=("Visitors", "sum"), Revenue=("Revenue_USD", "sum"),
             AvgStay=("Average_Stay_Days", "mean"))
        .reset_index()
    )


def get_stay_distribution(filters: dict | None = None) -> pd.Series:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return df["Average_Stay_Days"]


def get_rating_distribution(filters: dict | None = None) -> pd.Series:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return df["Customer_Rating"]


def get_repeat_visitor_stats(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    df["Visitor_Label"] = df["Repeat_Visitor"].map({1: "Repeat", 0: "New"})
    return (
        df.groupby("Visitor_Label")
        .agg(Count=("Tourist_ID", "count"), Visitors=("Visitors", "sum"),
             Revenue=("Revenue_USD", "sum"))
        .reset_index()
    )


def get_weather_impact(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby("Weather")
        .agg(Visitors=("Visitors", "sum"), Revenue=("Revenue_USD", "sum"),
             AvgRating=("Customer_Rating", "mean"))
        .reset_index()
    )


# ══════════════════════════════════════════════════════════════════════════
# HOTEL ANALYTICS
# ══════════════════════════════════════════════════════════════════════════

def get_occupancy_by_country(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby("Country")
        .agg(AvgOccupancy=("Hotel_Occupancy", "mean"),
             Visitors=("Visitors", "sum"),
             Revenue=("Revenue_USD", "sum"))
        .reset_index()
        .sort_values("AvgOccupancy", ascending=False)
    )


def get_occupancy_trend(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby(["Year", "Month"])
        .agg(AvgOccupancy=("Hotel_Occupancy", "mean"))
        .reset_index()
        .sort_values(["Year", "Month"])
    )


def get_occupancy_by_season(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby(["Season", "Accommodation_Type"])
        .agg(AvgOccupancy=("Hotel_Occupancy", "mean"),
             Revenue=("Revenue_USD", "sum"))
        .reset_index()
    )


def get_accommodation_performance(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return (
        df.groupby("Accommodation_Type")
        .agg(
            AvgOccupancy=("Hotel_Occupancy", "mean"),
            Revenue=("Revenue_USD", "sum"),
            Visitors=("Visitors", "sum"),
            AvgRating=("Customer_Rating", "mean"),
            AvgStay=("Average_Stay_Days", "mean"),
        )
        .reset_index()
        .sort_values("AvgOccupancy", ascending=False)
    )


# ══════════════════════════════════════════════════════════════════════════
# ADVANCED ANALYTICS
# ══════════════════════════════════════════════════════════════════════════

def get_correlation_matrix(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    num_cols = ["Visitors", "Revenue_USD", "Average_Stay_Days",
                "Hotel_Occupancy", "Customer_Rating", "Repeat_Visitor"]
    return df[num_cols].corr().round(3)


def get_numeric_data(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    return df[["Visitors", "Revenue_USD", "Average_Stay_Days",
               "Hotel_Occupancy", "Customer_Rating"]]


def get_outlier_data(filters: dict | None = None) -> pd.DataFrame:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)
    # IQR-based outlier flags
    for col in ["Visitors", "Revenue_USD"]:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        df[f"{col}_outlier"] = (df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)
    return df


def get_statistical_summary(filters: dict | None = None) -> pd.DataFrame:
    df = get_numeric_data(filters)
    return df.describe().round(2).reset_index().rename(columns={"index": "Statistic"})


def get_clustering_data(n_clusters: int = 4, filters: dict | None = None) -> pd.DataFrame:
    """K-Means clustering on country-level features."""
    try:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        return pd.DataFrame()

    country_df = get_country_stats(filters)
    if len(country_df) < n_clusters:
        return pd.DataFrame()

    features = ["Visitors", "Revenue", "AvgStay", "AvgRating", "AvgOccupancy"]
    X = country_df[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    country_df = country_df.copy()
    country_df["Cluster"] = km.fit_predict(X_scaled).astype(str)
    return country_df


# ══════════════════════════════════════════════════════════════════════════
# FORECASTING
# ══════════════════════════════════════════════════════════════════════════

def get_forecast_data(periods: int = 12, filters: dict | None = None) -> dict:
    """
    Simple moving-average + linear-trend forecast.
    Returns historical + forecast DataFrames.
    Falls back gracefully if data is insufficient.
    """
    monthly = get_monthly_visitors(filters)
    monthly = monthly.groupby(["Year", "Month"]).agg(
        Visitors=("Visitors", "sum"),
        Revenue=("Revenue", "sum")
    ).reset_index().sort_values(["Year", "Month"]).copy()

    if len(monthly) < 12:
        return {"error": "Insufficient data for forecasting (need ≥ 12 months)"}

    # Add period index
    monthly["Period"] = range(len(monthly))
    monthly["YearMonth"] = pd.to_datetime(
        monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)
    )

    # Linear trend forecast
    x = monthly["Period"].values
    yv = monthly["Visitors"].values
    yr = monthly["Revenue"].values

    v_coeffs = np.polyfit(x, yv, 1)
    r_coeffs = np.polyfit(x, yr, 1)

    last_period = monthly["Period"].max()
    last_date   = monthly["YearMonth"].max()

    future_periods = np.arange(last_period + 1, last_period + 1 + periods)
    future_dates   = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=periods, freq="MS")

    # Moving average for smoothing
    window = 6
    ma = monthly["Visitors"].rolling(window, min_periods=1).mean().iloc[-1]

    forecast_v = np.polyval(v_coeffs, future_periods)
    forecast_r = np.polyval(r_coeffs, future_periods)

    # Add 15% noise band for confidence interval
    ci_v = forecast_v * 0.15
    ci_r = forecast_r * 0.15

    forecast_df = pd.DataFrame({
        "YearMonth": future_dates,
        "Visitors": forecast_v.clip(min=0),
        "Revenue": forecast_r.clip(min=0),
        "Visitors_Lo": (forecast_v - ci_v).clip(min=0),
        "Visitors_Hi": (forecast_v + ci_v).clip(min=0),
        "Revenue_Lo": (forecast_r - ci_r).clip(min=0),
        "Revenue_Hi": (forecast_r + ci_r).clip(min=0),
        "Type": "Forecast",
    })

    monthly["Type"] = "Historical"
    monthly["Visitors_Lo"] = monthly["Visitors"]
    monthly["Visitors_Hi"] = monthly["Visitors"]
    monthly["Revenue_Lo"] = monthly["Revenue"]
    monthly["Revenue_Hi"] = monthly["Revenue"]

    return {"historical": monthly, "forecast": forecast_df}


# ══════════════════════════════════════════════════════════════════════════
# DATA EXPLORER
# ══════════════════════════════════════════════════════════════════════════

def get_explorer_data(
    page: int = 0,
    page_size: int = 20,
    search: str = "",
    sort_col: str = "Date",
    sort_dir: str = "desc",
    filters: dict | None = None,
) -> dict:
    df = get_df().copy()
    if filters:
        df = apply_filters(df, **filters)

    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df = df[mask]

    total = len(df)
    if sort_col in df.columns:
        df = df.sort_values(sort_col, ascending=(sort_dir == "asc"))

    page_df = df.iloc[page * page_size: (page + 1) * page_size].copy()
    # Convert Date back to string for display
    if "Date" in page_df.columns and hasattr(page_df["Date"], "dt"):
        page_df["Date"] = page_df["Date"].dt.strftime("%Y-%m-%d")

    return {
        "data": page_df.to_dict("records"),
        "total": total,
        "pages": max(1, -(-total // page_size)),
    }


def get_data_quality_stats() -> dict:
    df = get_df()
    return {
        "total_rows":   len(df),
        "total_cols":   len(df.columns),
        "missing":      int(df.isnull().sum().sum()),
        "duplicates":   int(df.duplicated().sum()),
        "date_range":   f"{df['Year'].min()} – {df['Year'].max()}",
        "countries":    df["Country"].nunique(),
        "cities":       df["City"].nunique(),
    }
