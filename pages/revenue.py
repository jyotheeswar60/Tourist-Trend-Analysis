"""
pages/revenue.py — Revenue Analytics page.
"""
import dash
from dash import html
from dash_iconify import DashIconify

dash.register_page(
    __name__,
    path="/revenue",
    name="Revenue Analytics",
    title="Tourism Analytics | Revenue Analytics",
    description="Revenue performance insights for tourism operations.",
    order=4,
)

layout = html.Div(
    className="page-enter",
    children=[
        html.Div(
            className="page-header",
            children=[
                html.Div(
                    className="page-header-top",
                    children=[
                        html.Div([
                            html.H1("Revenue Analytics", className="page-title"),
                            html.P(
                                "Analyze revenue performance, seasonality, and channel mix.",
                                className="page-subtitle",
                            ),
                        ]),
                    ],
                ),
            ],
        ),
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
                                icon="lucide:circle-dollar-sign",
                                width=32,
                                color="#6366F1",
                            ),
                        ),
                        html.H3(
                            "Revenue Analytics page coming soon",
                            className="empty-state-title",
                            style={"color": "#6366F1", "fontSize": "20px"},
                        ),
                        html.P(
                            "This page will highlight top revenue drivers and monthly performance.",
                            className="empty-state-text",
                            style={"maxWidth": "480px"},
                        ),
                    ],
                ),
            ],
        ),
    ],
)
