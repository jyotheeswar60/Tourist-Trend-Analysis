"""
pages/overview.py — Executive Overview (Page 1)
This is a PLACEHOLDER that validates the app shell runs correctly.
The full implementation follows in Module 2.
"""
import dash
from dash import html
from dash_iconify import DashIconify

dash.register_page(
    __name__,
    path="/",
    name="Executive Overview",
    title="Tourism Analytics | Executive Overview",
    description="High-level KPIs and executive summary for tourism trends.",
    order=1,
)


layout = html.Div(
    className="page-enter",
    children=[
        # Page header
        html.Div(
            className="page-header",
            children=[
                html.Div(
                    className="page-header-top",
                    children=[
                        html.Div([
                            html.H1("Executive Overview", className="page-title"),
                            html.P(
                                "High-level KPIs and performance summary across all destinations.",
                                className="page-subtitle",
                            ),
                        ]),
                        html.Div(
                            className="page-actions",
                            children=[
                                html.Button(
                                    className="btn btn-secondary btn-sm",
                                    children=[
                                        DashIconify(icon="lucide:download", width=14),
                                        html.Span("Export CSV"),
                                    ],
                                ),
                                html.Button(
                                    className="btn btn-primary btn-sm",
                                    children=[
                                        DashIconify(icon="lucide:sliders-horizontal", width=14),
                                        html.Span("Filters"),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),

        # Coming soon card (will be replaced in Module 2)
        html.Div(
            className="chart-card",
            style={"textAlign": "center", "padding": "80px 40px"},
            children=[
                html.Div(
                    className="empty-state",
                    children=[
                        html.Div(
                            className="empty-state-icon floating",
                            children=DashIconify(
                                icon="lucide:layout-dashboard",
                                width=32,
                                color="#6366F1",
                            ),
                        ),
                        html.H3(
                            "App Shell Running Successfully",
                            className="empty-state-title",
                            style={"color": "#6366F1", "fontSize": "20px"},
                        ),
                        html.P(
                            "The Dash app, sidebar, navbar, dark/light theme toggle, "
                            "and responsive layout are all working. "
                            "Module 2 will populate this page with KPI cards, "
                            "charts, and the full dashboard.",
                            className="empty-state-text",
                            style={"maxWidth": "480px"},
                        ),
                        html.Div(
                            style={"marginTop": "24px", "display": "flex",
                                   "gap": "12px", "justifyContent": "center",
                                   "flexWrap": "wrap"},
                            children=[
                                html.Span(
                                    className="badge badge-primary",
                                    children=f"✓  {item['label']}",
                                )
                                for item in [
                                    {"label": "Dark/Light Mode"},
                                    {"label": "Sidebar Toggle"},
                                    {"label": "Active Nav States"},
                                    {"label": "Responsive Layout"},
                                    {"label": "Premium CSS"},
                                    {"label": "Multi-page Routing"},
                                ]
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)
