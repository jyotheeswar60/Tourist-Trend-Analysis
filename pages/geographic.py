"""
pages/geographic.py — Geographic Analysis page.
"""
import dash
from dash import html
from dash_iconify import DashIconify

dash.register_page(
    __name__,
    path="/geographic",
    name="Geographic Analysis",
    title="Tourism Analytics | Geographic Analysis",
    description="Geographic distribution of tourism metrics across regions.",
    order=3,
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
                            html.H1("Geographic Analysis", className="page-title"),
                            html.P(
                                "Discover where tourism demand is highest across destinations.",
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
                                icon="lucide:globe-2",
                                width=32,
                                color="#6366F1",
                            ),
                        ),
                        html.H3(
                            "Geographic Analysis page coming soon",
                            className="empty-state-title",
                            style={"color": "#6366F1", "fontSize": "20px"},
                        ),
                        html.P(
                            "This page will show regional tourism performance and map visualizations.",
                            className="empty-state-text",
                            style={"maxWidth": "480px"},
                        ),
                    ],
                ),
            ],
        ),
    ],
)
