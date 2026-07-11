"""pages/visitor_behavior.py — Visitor Behavior Analytics."""
import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from dash_iconify import DashIconify
from services.data_service import (
    get_by_purpose, get_by_transport, get_by_accommodation,
    get_stay_distribution, get_rating_distribution, get_repeat_visitor_stats,
    get_weather_impact, get_type_trends, get_filter_options
)
from utils.chart_themes import themed_layout, PRIMARY_COLORS, TYPE_COLORS
from utils.chart_config import GRAPH_CONFIG
import numpy as np

dash.register_page(__name__, path="/visitor-behavior", name="Visitor Behavior",
                   title="Tourism Analytics | Visitor Behavior", order=5)

_opts = get_filter_options()
YEAR_OPTS    = [{"label": str(y), "value": y} for y in _opts["years"]]
COUNTRY_OPTS = [{"label": c, "value": c} for c in _opts["countries"]]
TYPE_OPTS    = [{"label": t, "value": t} for t in _opts["tourist_types"]]

layout = html.Div(className="page-enter", children=[
    html.Div(className="page-header", children=[
        html.Div(className="page-header-top", children=[
            html.Div([
                html.H1("Visitor Behavior", className="page-title"),
                html.P("Demographics, preferences, and travel patterns", className="page-subtitle"),
            ]),
        ]),
    ]),

    # Filters
    html.Div(className="filter-panel", children=[
        html.Div(className="filter-row", children=[
            html.Div(className="filter-group", children=[
                html.Label("Year", className="filter-label"),
                dcc.Dropdown(id="vb-year-filter", options=YEAR_OPTS, multi=True, placeholder="All Years", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Country", className="filter-label"),
                dcc.Dropdown(id="vb-country-filter", options=COUNTRY_OPTS, multi=True, placeholder="All Countries", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Tourist Type", className="filter-label"),
                dcc.Dropdown(id="vb-type-filter", options=TYPE_OPTS, multi=True, placeholder="All Types", className="filter-dropdown"),
            ]),
        ]),
    ]),

    # KPI Row
    html.Div(className="kpi-grid", style={"gridTemplateColumns":"repeat(4,1fr)"}, children=[
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Avg Stay Days", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:calendar-clock", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="vb-kpi-avg-stay"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Avg Rating", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:star", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="vb-kpi-avg-rating"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Repeat Visitor %", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:refresh-cw", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="vb-kpi-repeat-pct"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Top Purpose", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:briefcase", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="vb-kpi-top-purpose"),
        ]),
    ]),

    # Purpose & Type
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Travel Purpose", className="chart-card-title")]),
            dcc.Graph(id="vb-purpose-chart", config=GRAPH_CONFIG, style={"height": "380px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Tourist Type", className="chart-card-title")]),
            dcc.Graph(id="vb-type-donut", config=GRAPH_CONFIG, style={"height": "380px"}),
        ]),
    ]),

    # 3-col split: Transport, Accom, Repeat
    html.Div(className="chart-grid", style={"gridTemplateColumns":"repeat(3,1fr)"}, children=[
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("Transport Mode", className="chart-card-title")]),
            dcc.Graph(id="vb-transport-chart", config=GRAPH_CONFIG, style={"height": "340px"}),
        ]),
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("Accommodation", className="chart-card-title")]),
            dcc.Graph(id="vb-accom-chart", config=GRAPH_CONFIG, style={"height": "340px"}),
        ]),
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("New vs Repeat", className="chart-card-title")]),
            dcc.Graph(id="vb-repeat-chart", config=GRAPH_CONFIG, style={"height": "340px"}),
        ]),
    ]),

    # Histograms
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Stay Duration Distribution", className="chart-card-title")]),
            dcc.Graph(id="vb-stay-hist", config=GRAPH_CONFIG, style={"height": "380px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Rating Distribution", className="chart-card-title")]),
            dcc.Graph(id="vb-rating-hist", config=GRAPH_CONFIG, style={"height": "380px"}),
        ]),
    ]),

    # Weather
    html.Div(className="chart-card", children=[
        html.Div(className="chart-card-header", children=[html.Span("Weather Impact on Visitors", className="chart-card-title")]),
        dcc.Graph(id="vb-weather-chart", config=GRAPH_CONFIG, style={"height": "380px"}),
    ]),

    # Insights
    html.Div(className="chart-card", id="vb-insights"),
])


@dash.callback(
    [Output("vb-kpi-avg-stay", "children"),
     Output("vb-kpi-avg-rating", "children"),
     Output("vb-kpi-repeat-pct", "children"),
     Output("vb-kpi-top-purpose", "children"),
     Output("vb-purpose-chart", "figure"),
     Output("vb-type-donut", "figure"),
     Output("vb-transport-chart", "figure"),
     Output("vb-accom-chart", "figure"),
     Output("vb-repeat-chart", "figure"),
     Output("vb-stay-hist", "figure"),
     Output("vb-rating-hist", "figure"),
     Output("vb-weather-chart", "figure"),
     Output("vb-insights", "children")],
    [Input("vb-year-filter", "value"),
     Input("vb-country-filter", "value"),
     Input("vb-type-filter", "value")],
    prevent_initial_call=False,
)
def update_vb(years, countries, types):
    f = {}
    if years: f["years"] = years
    if countries: f["countries"] = countries
    if types: f["tourist_types"] = types
    filters = f or None

    purpose_df   = get_by_purpose(filters)
    transport_df = get_by_transport(filters)
    accom_df     = get_by_accommodation(filters)
    repeat_df    = get_repeat_visitor_stats(filters)
    weather_df   = get_weather_impact(filters)
    type_df      = get_type_trends(filters)
    stay_s       = get_stay_distribution(filters)
    rating_s     = get_rating_distribution(filters)

    avg_stay = stay_s.mean() if not stay_s.empty else 0
    avg_rate = rating_s.mean() if not rating_s.empty else 0
    top_purp = purpose_df.iloc[0]["Travel_Purpose"] if not purpose_df.empty else "N/A"
    
    rep_pct = 0
    if not repeat_df.empty:
        total = repeat_df["Count"].sum()
        rep   = repeat_df[repeat_df["Visitor_Label"] == "Repeat"]["Count"].sum()
        rep_pct = (rep / total * 100) if total else 0

    # Purpose
    fig_purp = go.Figure()
    if not purpose_df.empty:
        pdf = purpose_df.sort_values("Visitors", ascending=True)
        fig_purp.add_trace(go.Bar(
            y=pdf["Travel_Purpose"], x=pdf["Visitors"], orientation="h", marker_color="#6366F1"
        ))
    fig_purp.update_layout(**themed_layout(True))

    # Type
    fig_type = go.Figure()
    if not type_df.empty:
        tdf = type_df.groupby("Tourist_Type")["Visitors"].sum().reset_index()
        fig_type.add_trace(go.Pie(
            labels=tdf["Tourist_Type"], values=tdf["Visitors"], hole=0.5,
            marker=dict(colors=[TYPE_COLORS.get(t, "#6366F1") for t in tdf["Tourist_Type"]])
        ))
    fig_type.update_layout(**themed_layout(True))

    # Transport
    fig_trans = go.Figure()
    if not transport_df.empty:
        fig_trans.add_trace(go.Pie(
            labels=transport_df["Transport_Mode"], values=transport_df["Visitors"],
            marker=dict(colors=PRIMARY_COLORS)
        ))
    fig_trans.update_layout(**themed_layout(True))

    # Accom
    fig_acc = go.Figure()
    if not accom_df.empty:
        adf = accom_df.sort_values("Visitors", ascending=True)
        fig_acc.add_trace(go.Bar(
            y=adf["Accommodation_Type"], x=adf["Visitors"], orientation="h", marker_color="#10B981"
        ))
    fig_acc.update_layout(**themed_layout(True))

    # Repeat
    fig_rep = go.Figure()
    if not repeat_df.empty:
        fig_rep.add_trace(go.Pie(
            labels=repeat_df["Visitor_Label"], values=repeat_df["Count"], hole=0.5,
            marker=dict(colors=["#3B82F6", "#94A3B8"])
        ))
    fig_rep.update_layout(**themed_layout(True))

    # Stay Hist
    fig_stay = go.Figure()
    if not stay_s.empty:
        fig_stay.add_trace(go.Histogram(
            x=stay_s, nbinsx=20, marker_color="#F59E0B"
        ))
    fig_stay.update_layout(**themed_layout(True), xaxis_title="Days", yaxis_title="Count")

    # Rating Hist
    fig_rat = go.Figure()
    if not rating_s.empty:
        fig_rat.add_trace(go.Histogram(
            x=rating_s, nbinsx=10, marker_color="#EF4444"
        ))
    fig_rat.update_layout(**themed_layout(True), xaxis_title="Rating (1-5)", yaxis_title="Count")

    # Weather
    fig_wea = go.Figure()
    if not weather_df.empty:
        wdf = weather_df.sort_values("Visitors", ascending=False)
        fig_wea.add_trace(go.Bar(
            x=wdf["Weather"], y=wdf["Visitors"], marker_color="#06B6D4"
        ))
    fig_wea.update_layout(**themed_layout(True), xaxis_title="Weather Condition", yaxis_title="Visitors")

    insights = html.Div([
        html.Div(className="chart-card-header", children=[html.Span("💡 Behavior Insights", className="chart-card-title")]),
        html.Div(style={"display":"flex","flexWrap":"wrap","gap":"12px","padding":"16px"}, children=[
            html.Div(className="insight-item", children=[html.Span("🎯", className="insight-icon"), html.Span(f"Top Purpose: {top_purp}.", className="insight-text")]),
            html.Div(className="insight-item", children=[html.Span("⭐", className="insight-icon"), html.Span(f"Average Rating: {avg_rate:.2f}.", className="insight-text")]),
        ]),
    ])

    return (
        f"{avg_stay:.1f}",
        f"{avg_rate:.2f}",
        f"{rep_pct:.1f}%",
        top_purp,
        fig_purp, fig_type, fig_trans, fig_acc, fig_rep, fig_stay, fig_rat, fig_wea, insights
    )
