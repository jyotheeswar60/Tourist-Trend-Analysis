"""
pages/hotel.py — Hotel Analytics page.
"""
import dash
from dash import html
from dash_iconify import DashIconify

dash.register_page(
    __name__,
    path="/hotel",
    name="Hotel Analytics",
    title="Tourism Analytics | Hotel Analytics",
    description="Hotel performance metrics for occupancy, pricing, and guest satisfaction.",
    order=6,
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
                            html.H1("Hotel Analytics", className="page-title"),
                            html.P(
                                "Track occupancy, revenue per available room, and guest satisfaction.",
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
                                icon="lucide:hotel",
                                width=32,
                                color="#6366F1",
                            ),
                        ),
                        html.H3(
                            "Hotel Analytics page coming soon",
                            className="empty-state-title",
                            style={"color": "#6366F1", "fontSize": "20px"},
                        ),
                        html.P(
                            "This page will surface hotel occupancy and revenue insights.",
                            className="empty-state-text",
                            style={"maxWidth": "480px"},
                        ),
                    ],
                ),
            ],
        ),
    ],
)
