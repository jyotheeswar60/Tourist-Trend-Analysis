"""
app.py — Tourism Analytics Platform entry point.

This file does exactly three things:
  1. Creates the Dash application instance (the "factory")
  2. Defines the top-level layout (navbar + sidebar + page container)
  3. Registers all cross-page callbacks (theme, sidebar toggle, nav active states)

Every page in pages/ registers itself with dash.register_page().
dash.page_container renders the current page's layout automatically.

Run locally:
    python app.py
    → http://localhost:8050

Production:
    gunicorn wsgi:server
"""
from __future__ import annotations

import json
import logging

import dash
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, clientside_callback, dcc, html
from dash_iconify import DashIconify

from components.navbar import create_navbar
from components.sidebar import NAV_ITEMS, create_sidebar
from config import config

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION FACTORY
# ─────────────────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    use_pages=True,                   # Auto-discover files in pages/
    pages_folder="pages",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,         # Reset + grid utilities
    ],
    suppress_callback_exceptions=True,  # Required for multi-page apps
    meta_tags=[
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1, shrink-to-fit=no",
        },
        {
            "name": "description",
            "content": "Tourism Trends Analytics Platform — Interactive BI Dashboard",
        },
        {"name": "theme-color", "content": "#6366F1"},
    ],
    title=config.APP_TITLE,
    update_title=None,                # Disable "Updating..." title flicker
)

# Expose Flask server for Gunicorn
server = app.server


# ─────────────────────────────────────────────────────────────────────────────
# TOP-LEVEL LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
app.layout = html.Div(
    id="app-container",
    className="dark-mode",      # Default theme
    children=[
        # ── Background Layers ────────────────────────────────────────────
        html.Div(
            className="bg-layer-container",
            children=[
                html.Div(className="bg-image"),
                html.Div(className="bg-glow-layer"),
                html.Div(className="bg-routes"),
                html.Div(className="bg-particles"),
                html.Div(className="bg-light-sweep"),
                html.Div(className="bg-overlay"),
            ]
        ),

        # ── Client-side State Stores ─────────────────────────────────────
        # dcc.Store persists data in the browser session without a round-trip.
        # Using storage_type="session" so state survives page refresh.
        dcc.Store(id="sidebar-store", data="expanded", storage_type="session"),
        dcc.Store(id="filter-store",  data={},         storage_type="memory"),

        # URL tracker — required for active nav state + page title
        dcc.Location(id="url", refresh=False),

        # ── Navigation Shell ──────────────────────────────────────────────
        create_navbar(),

        # ── Body: Sidebar + Page Content ──────────────────────────────────
        html.Div(
            className="app-body",
            children=[
                create_sidebar(),
                html.Main(
                    id="page-content",
                    className="page-content",
                    children=[
                        # dash.page_container renders the active page
                        dash.page_container,
                    ],
                ),
            ],
        ),
    ],
)





# ─────────────────────────────────────────────────────────────────────────────
# CALLBACK 2: SIDEBAR TOGGLE (server-side)
# Adds/removes "collapsed" class on the sidebar and adjusts page-content margin.
# ─────────────────────────────────────────────────────────────────────────────
@app.callback(
    Output("sidebar", "className"),
    Output("page-content", "className"),
    Output("sidebar-store", "data"),
    Input("sidebar-toggle-btn", "n_clicks"),
    State("sidebar-store", "data"),
    prevent_initial_call=True,
)
def toggle_sidebar(n_clicks: int, state: str):
    """Collapse or expand the sidebar."""
    if state == "expanded":
        log.debug("Sidebar → collapsed")
        return "sidebar collapsed", "page-content sidebar-collapsed", "collapsed"
    log.debug("Sidebar → expanded")
    return "sidebar", "page-content", "expanded"


# ─────────────────────────────────────────────────────────────────────────────
# CALLBACK 3: ACTIVE NAV ITEM + PAGE TITLE (clientside — runs in browser)
# Comparing the current URL to each nav item's href.
# A clientside callback runs JavaScript directly, avoiding a Python roundtrip.
# This is the correct pattern for UI-only updates.
# ─────────────────────────────────────────────────────────────────────────────

# Flatten all nav items into a list for the clientside callback
ALL_NAV_ITEMS = [item for section in NAV_ITEMS for item in section["items"]]
NAV_IDS       = [item["id"]    for item in ALL_NAV_ITEMS]
NAV_HREFS     = [item["href"]  for item in ALL_NAV_ITEMS]
NAV_LABELS    = [item["label"] for item in ALL_NAV_ITEMS]

clientside_callback(
    f"""
    function(pathname) {{
        const navIds = {json.dumps(NAV_IDS)};
        const navHrefs = {json.dumps(NAV_HREFS)};
        const navLabels = {json.dumps(NAV_LABELS)};

        let pageTitle = "Tourism Analytics";

        navHrefs.forEach(function(href, idx) {{
            const el = document.getElementById(navIds[idx]);
            if (!el) return;

            const isActive = (href === '/') ? (pathname === '/') : pathname.startsWith(href);
            if (isActive) {{
                el.classList.add('active');
                pageTitle = navLabels[idx];
            }} else {{
                el.classList.remove('active');
            }}
        }});

        return pageTitle;
    }}
    """,
    Output("navbar-page-title", "children"),
    Input("url", "pathname"),
    prevent_initial_call=False,
)


# ─────────────────────────────────────────────────────────────────────────────
# CALLBACK 4: KPI COUNTER ANIMATION (clientside)
# Animates numeric KPI values from 0 to their target value using
# requestAnimationFrame for silky-smooth, non-blocking animation.
# The data-target attribute is set by the server; JS reads it and animates.
# ─────────────────────────────────────────────────────────────────────────────
# NOTE: KPI counter animation is triggered per-page via a dedicated
# clientside_callback defined in each page that has KPI cards.
# The animation function is defined in assets/animations.css (JS equivalent)
# and called with: window.animateKPI(elementId, targetValue, prefix, suffix)



# ─────────────────────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info(f"Starting {config.APP_TITLE} on http://{config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        dev_tools_hot_reload=config.DEBUG,
    )
