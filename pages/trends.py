"""
pages/trends.py — Tourism Trends page.
"""
import dash
from dash import html
from dash_iconify import DashIconify

dash.register_page(
    __name__,
    path="/trends",
    name="Tourism Trends",
    title="Tourism Analytics | Tourism Trends",
    description="Trend analysis for visitor counts, revenue, and seasonality.",
    order=2,
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
                            html.H1("Tourism Trends", className="page-title"),
                            html.P(
                                "Explore trend patterns in visitor numbers and tourism revenue.",
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
                                icon="lucide:trending-up",
                                width=32,
                                color="#6366F1",
                            ),
                        ),
                        html.H3(
                            "Tourism Trends page coming soon",
                            className="empty-state-title",
                            style={"color": "#6366F1", "fontSize": "20px"},
                        ),
                        html.P(
                            "This page will display revenue and visitor trend analytics with interactive charts.",
                            className="empty-state-text",
                            style={"maxWidth": "480px"},
                        ),
                    ],
                ),
            ],
        ),
    ],
)
