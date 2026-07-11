"""
pages/visitor_behavior.py — Visitor Behavior page.
"""
import dash
from dash import html
from dash_iconify import DashIconify

dash.register_page(
    __name__,
    path="/visitor-behavior",
    name="Visitor Behavior",
    title="Tourism Analytics | Visitor Behavior",
    description="Insights on visitor demographics, stay length, and booking behavior.",
    order=5,
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
                            html.H1("Visitor Behavior", className="page-title"),
                            html.P(
                                "Understand guest preferences, stay duration, and repeat visits.",
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
                                icon="lucide:users-2",
                                width=32,
                                color="#6366F1",
                            ),
                        ),
                        html.H3(
                            "Visitor Behavior page coming soon",
                            className="empty-state-title",
                            style={"color": "#6366F1", "fontSize": "20px"},
                        ),
                        html.P(
                            "This page will measure visitor segments, loyalty, and engagement.",
                            className="empty-state-text",
                            style={"maxWidth": "480px"},
                        ),
                    ],
                ),
            ],
        ),
    ],
)
