"""
pages/explorer.py — Data Explorer page.
"""
import dash
from dash import html
from dash_iconify import DashIconify

dash.register_page(
    __name__,
    path="/explorer",
    name="Data Explorer",
    title="Tourism Analytics | Data Explorer",
    description="Interactive data exploration tools for tourism datasets.",
    order=9,
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
                            html.H1("Data Explorer", className="page-title"),
                            html.P(
                                "Explore raw tourism data and inspect underlying records.",
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
                                icon="lucide:table-2",
                                width=32,
                                color="#6366F1",
                            ),
                        ),
                        html.H3(
                            "Data Explorer page coming soon",
                            className="empty-state-title",
                            style={"color": "#6366F1", "fontSize": "20px"},
                        ),
                        html.P(
                            "This page will provide exploratory tools for the tourism dataset.",
                            className="empty-state-text",
                            style={"maxWidth": "480px"},
                        ),
                    ],
                ),
            ],
        ),
    ],
)
