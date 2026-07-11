"""
components/navbar.py — Top navigation bar.

Responsibilities:
  • Sidebar toggle button (hamburger icon)
  • Dynamic page title (updated via callback when URL changes)
  • Live data indicator badge
  • Theme toggle (dark ↔ light)
  • User avatar

All interactive elements use IDs consumed by callbacks in callbacks/theme.py
and callbacks/navigation.py.
"""
from dash import html, dcc
from dash_iconify import DashIconify


def create_navbar() -> html.Div:
    """Return the fixed top navigation bar component."""
    return html.Div(
        className="top-navbar",
        children=[
            # ── Left Section ─────────────────────────────────────────────
            html.Div(
                className="navbar-left",
                children=[
                    # Hamburger / sidebar toggle
                    html.Button(
                        id="sidebar-toggle-btn",
                        className="navbar-toggle-btn",
                        title="Toggle sidebar",
                        n_clicks=0,
                        children=DashIconify(icon="lucide:menu", width=18),
                    ),
                    # Vertical divider
                    html.Div(className="navbar-divider"),
                    # Dynamic breadcrumb / page title
                    html.Div(
                        id="navbar-page-title",
                        className="navbar-page-title",
                        children="Executive Overview",
                    ),
                ],
            ),

            # ── Right Section ────────────────────────────────────────────
            html.Div(
                className="navbar-right",
                children=[
                    # Live indicator
                    html.Div(
                        className="navbar-live-badge",
                        title="Data is up to date",
                        children=[
                            html.Div(className="navbar-live-dot"),
                            html.Span("Live"),
                        ],
                    ),

                    # Refresh button
                    html.Button(
                        id="refresh-btn",
                        className="navbar-icon-btn",
                        title="Refresh data",
                        n_clicks=0,
                        children=DashIconify(icon="lucide:refresh-cw", width=16),
                    ),

                    # Divider
                    html.Div(className="navbar-divider"),

                    # Theme toggle
                    html.Button(
                        id="theme-toggle-btn",
                        className="navbar-icon-btn",
                        title="Toggle theme",
                        n_clicks=0,
                        children=DashIconify(
                            id="theme-toggle-icon",
                            icon="lucide:sun",
                            width=17,
                        ),
                    ),

                    # User avatar
                    html.Div(
                        className="navbar-avatar",
                        title="Portfolio Project",
                        children="TA",
                    ),
                ],
            ),
        ],
    )
