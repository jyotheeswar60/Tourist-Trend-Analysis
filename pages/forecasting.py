"""
pages/forecasting.py — Forecasting page.
"""
import dash
from dash import html
from dash_iconify import DashIconify

dash.register_page(
    __name__,
    path="/forecasting",
    name="Forecasting",
    title="Tourism Analytics | Forecasting",
    description="Forecast future travel demand and revenue trends.",
    order=8,
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
                            html.H1("Forecasting", className="page-title"),
                            html.P(
                                "Predict future tourism demand with trend-based forecasting.",
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
                                icon="lucide:brain-circuit",
                                width=32,
                                color="#6366F1",
                            ),
                        ),
                        html.H3(
                            "Forecasting page coming soon",
                            className="empty-state-title",
                            style={"color": "#6366F1", "fontSize": "20px"},
                        ),
                        html.P(
                            "This page will present future projections for tourism KPIs.",
                            className="empty-state-text",
                            style={"maxWidth": "480px"},
                        ),
                    ],
                ),
            ],
        ),
    ],
)
