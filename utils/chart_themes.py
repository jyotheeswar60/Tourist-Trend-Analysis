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

def _make_layout(is_dark: bool = True) -> dict:
    bg     = DARK_BG
    paper  = DARK_PAPER
    grid   = DARK_GRID
    text   = DARK_TEXT
    title  = DARK_TITLE

    return dict(
        paper_bgcolor=paper,
        plot_bgcolor="rgba(0,0,0,0)", # transparent background to show through glassmorphism
        font=dict(family="Inter, sans-serif", color=text, size=12),
        title_font=dict(family="Inter, sans-serif", color=title, size=15, weight="bold"),
        xaxis=dict(
            gridcolor=grid, gridwidth=1,
            linecolor=grid, tickcolor=grid,
            title_font=dict(color=text), tickfont=dict(color=text),
            zeroline=False,
            showspikes=True, spikecolor=grid, spikethickness=1,
        ),
        yaxis=dict(
            gridcolor=grid, gridwidth=1,
            linecolor=grid, tickcolor=grid,
            title_font=dict(color=text), tickfont=dict(color=text),
            zeroline=False,
            showspikes=True, spikecolor=grid, spikethickness=1,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=text),
            borderwidth=0,
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        colorway=PRIMARY_COLORS,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 41, 0.9)",
            font_color="#F1F5F9",
            bordercolor="#6366F1",
            font_family="Inter",
        ),
        modebar=dict(bgcolor="rgba(0,0,0,0)", color=text),
        transition=dict(duration=700, easing="cubic-in-out"),
    )


def apply_theme(fig: go.Figure, is_dark: bool = True) -> go.Figure:
    """Apply dark theme to a Plotly figure."""
    fig.update_layout(**_make_layout(is_dark))
    return fig


def themed_layout(is_dark: bool = True) -> dict:
    """Return dark layout dict for use in go.Figure(layout=...)."""
    return _make_layout(is_dark)


def apply_empty_state_annotation(fig: go.Figure) -> go.Figure:
    """Add a centered 'No data available' message to an empty chart."""
    fig.update_layout(**_make_layout(True))
    fig.add_annotation(
        text="No data available for the selected filters",
        showarrow=False,
        font=dict(size=14, color="#94A3B8")
    )
    return fig
