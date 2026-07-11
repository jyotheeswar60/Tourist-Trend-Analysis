"""
utils/chart_themes.py — Shared Plotly theme and color config.

All charts import DARK_TEMPLATE and LIGHT_TEMPLATE to ensure
visual consistency across all 9 pages.
"""
from __future__ import annotations
import plotly.graph_objects as go
import plotly.io as pio

# ── Color Palettes ─────────────────────────────────────────────────────────
PRIMARY_COLORS = [
    "#6366F1", "#10B981", "#F59E0B", "#3B82F6", "#EF4444",
    "#8B5CF6", "#06B6D4", "#EC4899", "#14B8A6", "#F97316",
]

SEQUENTIAL_BLUE  = "Blues"
SEQUENTIAL_PURP  = "Purples"
DIVERGING        = "RdYlGn"

SEASON_COLORS = {
    "Spring": "#10B981",
    "Summer": "#F59E0B",
    "Autumn": "#F97316",
    "Winter": "#3B82F6",
}

TYPE_COLORS = {
    "Leisure":   "#6366F1",
    "Business":  "#3B82F6",
    "Adventure": "#10B981",
    "Cultural":  "#F59E0B",
    "Medical":   "#EF4444",
}

# ── Dark Template ──────────────────────────────────────────────────────────
DARK_BG        = "#0F1729"
DARK_PAPER     = "#141E33"
DARK_GRID      = "rgba(255,255,255,0.06)"
DARK_TEXT      = "#94A3B8"
DARK_TITLE     = "#F1F5F9"

# ── Light Template ─────────────────────────────────────────────────────────
LIGHT_BG       = "#F8FAFC"
LIGHT_PAPER    = "#FFFFFF"
LIGHT_GRID     = "rgba(0,0,0,0.06)"
LIGHT_TEXT     = "#64748B"
LIGHT_TITLE    = "#0F172A"


def _make_layout(is_dark: bool) -> dict:
    bg     = DARK_BG     if is_dark else LIGHT_BG
    paper  = DARK_PAPER  if is_dark else LIGHT_PAPER
    grid   = DARK_GRID   if is_dark else LIGHT_GRID
    text   = DARK_TEXT   if is_dark else LIGHT_TEXT
    title  = DARK_TITLE  if is_dark else LIGHT_TITLE

    return dict(
        paper_bgcolor=paper,
        plot_bgcolor=bg,
        font=dict(family="Inter, sans-serif", color=text, size=12),
        title_font=dict(family="Inter, sans-serif", color=title, size=15, weight="bold"),
        xaxis=dict(
            gridcolor=grid, gridwidth=1,
            linecolor=grid, tickcolor=grid,
            title_font=dict(color=text), tickfont=dict(color=text),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=grid, gridwidth=1,
            linecolor=grid, tickcolor=grid,
            title_font=dict(color=text), tickfont=dict(color=text),
            zeroline=False,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)" if is_dark else "rgba(255,255,255,0)",
            font=dict(color=text),
            borderwidth=0,
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        colorway=PRIMARY_COLORS,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1E293B" if is_dark else "#FFFFFF",
            font_color="#F1F5F9" if is_dark else "#0F172A",
            bordercolor="#6366F1",
        ),
        modebar=dict(bgcolor="rgba(0,0,0,0)", color=text),
    )


def apply_theme(fig: go.Figure, is_dark: bool = True) -> go.Figure:
    """Apply dark or light theme to a Plotly figure."""
    fig.update_layout(**_make_layout(is_dark))
    return fig


def themed_layout(is_dark: bool = True) -> dict:
    """Return layout dict for use in go.Figure(layout=...)."""
    return _make_layout(is_dark)
