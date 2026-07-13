"""
components/sidebar.py — Collapsible left sidebar navigation.

Structure:
  • Logo / brand mark at top
  • Two nav sections: ANALYTICS and INSIGHTS
  • Each nav item: icon + label + active state
  • Footer with version number

Sidebar state (expanded / collapsed) is stored in dcc.Store("sidebar-state")
and toggled by the callback in callbacks/navigation.py.

The active nav item is determined by the current URL, handled via dcc.Location
and a clientside callback that adds/removes the "active" class.
"""
from dash import html, dcc
from dash_iconify import DashIconify


# ── Navigation item definitions ────────────────────────────────────────────
# icon: Iconify string (lucide icon set)
# label: Human-readable page name
# href: URL path registered in each page file
# id: used for active-state detection
NAV_ITEMS = [
    # ── Section 1: ANALYTICS ──────────────────────────────────────────────
    {
        "section": "ANALYTICS",
        "items": [
            {
                "icon": "lucide:layout-dashboard",
                "label": "Executive Overview",
                "href": "/",
                "id": "nav-overview",
            },
            {
                "icon": "lucide:trending-up",
                "label": "Tourism Trends",
                "href": "/trends",
                "id": "nav-trends",
            },
            {
                "icon": "lucide:globe-2",
                "label": "Geographic Analysis",
                "href": "/geographic",
                "id": "nav-geographic",
            },
            {
                "icon": "lucide:circle-dollar-sign",
                "label": "Revenue Analytics",
                "href": "/revenue",
                "id": "nav-revenue",
            },
        ],
    },
    # ── Section 2: INSIGHTS ───────────────────────────────────────────────
    {
        "section": "INSIGHTS",
        "items": [
            {
                "icon": "lucide:users-2",
                "label": "Visitor Behavior",
                "href": "/visitor-behavior",
                "id": "nav-visitor",
            },
            {
                "icon": "lucide:hotel",
                "label": "Hotel Analytics",
                "href": "/hotel",
                "id": "nav-hotel",
            },
            {
                "icon": "lucide:bar-chart-3",
                "label": "Advanced Analytics",
                "href": "/advanced",
                "id": "nav-advanced",
            },
            {
                "icon": "lucide:brain-circuit",
                "label": "Forecasting",
                "href": "/forecasting",
                "id": "nav-forecast",
            },
            {
                "icon": "lucide:table-2",
                "label": "Data Explorer",
                "href": "/explorer",
                "id": "nav-explorer",
            },
        ],
    },
]


def _nav_item(icon: str, label: str, href: str, item_id: str) -> html.A:
    """
    Build a single navigation link element.

    Uses html.A (anchor tag) for proper URL routing with dash.page_container.
    The "active" class is applied / removed by a clientside callback
    that compares pathname to href.
    """
    return html.A(
        id=item_id,
        href=href,
        className="nav-item",
        children=[
            html.Span(
                className="nav-item-icon",
                children=DashIconify(icon=icon, width=18),
            ),
            html.Span(className="nav-item-label", children=label),
        ],
    )


def create_sidebar() -> html.Div:
    """
    Return the full sidebar component.

    The sidebar div has id="sidebar" so the toggle callback in
    callbacks/navigation.py can update its className between
    "sidebar" (expanded) and "sidebar collapsed".
    """
    nav_sections = []
    for section in NAV_ITEMS:
        nav_sections.append(
            html.Div(
                className="nav-section-label",
                children=section["section"],
            )
        )
        for item in section["items"]:
            nav_sections.append(
                _nav_item(
                    icon=item["icon"],
                    label=item["label"],
                    href=item["href"],
                    item_id=item["id"],
                )
            )

    return html.Div(
        id="sidebar",
        className="sidebar",
        children=[

            # ── Logo ─────────────────────────────────────────────────────
            html.Div(
                className="sidebar-logo",
                children=[
                    html.Div(
                        className="sidebar-logo-icon-wrap",
                        children=DashIconify(
                            icon="lucide:globe",
                            width=18,
                            color="white",
                        ),
                    ),
                    html.Span(
                        className="sidebar-logo-text",
                        children="Tourism Analytics",
                    ),
                ],
            ),

            # ── Navigation ───────────────────────────────────────────────
            html.Nav(
                className="sidebar-nav",
                children=nav_sections,
            ),
        ],
    )
