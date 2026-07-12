"""pages/forecasting.py — Forecasting Analytics."""
import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
from dash_iconify import DashIconify
from services.data_service import get_forecast_data, get_filter_options
from utils.chart_themes import themed_layout
from utils.chart_config import GRAPH_CONFIG
import pandas as pd

dash.register_page(__name__, path="/forecasting", name="Forecasting",
                   title="Tourism Analytics | Forecasting", order=8)

_opts = get_filter_options()
COUNTRY_OPTS = [{"label": c, "value": c} for c in _opts["countries"]]
TYPE_OPTS    = [{"label": t, "value": t} for t in _opts["tourist_types"]]

layout = html.Div(className="page-enter", children=[
    html.Div(className="page-header", children=[
        html.Div(className="page-header-top", children=[
            html.Div([
                html.H1("Forecasting", className="page-title"),
                html.P("Predictive models for visitor volumes and revenue", className="page-subtitle"),
            ]),
        ]),
    ]),

    # Filters
    html.Div(className="filter-panel", children=[
        html.Div(className="filter-row", children=[
            html.Div(className="filter-group", children=[
                html.Label("Country", className="filter-label"),
                dcc.Dropdown(id="fc-country-filter", options=COUNTRY_OPTS, multi=True, placeholder="All Countries", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Tourist Type", className="filter-label"),
                dcc.Dropdown(id="fc-type-filter", options=TYPE_OPTS, multi=True, placeholder="All Types", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", style={"flex":"2"}, children=[
                html.Label("Forecast Periods (Months)", className="filter-label"),
                dcc.Slider(id="fc-periods-slider", min=6, max=24, step=6, value=12,
                           marks={6:"6M", 12:"1Y", 18:"18M", 24:"2Y"}),
            ]),
        ]),
    ]),

    # KPI Row
    html.Div(className="kpi-grid", style={"gridTemplateColumns":"repeat(4,1fr)"}, children=[
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Forecast Period", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:clock", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="fc-kpi-periods"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Projected Visitors (End)", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:users", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="fc-kpi-proj-visitors"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Projected Revenue (End)", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:dollar-sign", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="fc-kpi-proj-revenue"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Forecast Trend", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:trending-up", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="fc-kpi-trend"),
        ]),
    ]),

    # Error msg (if insufficient data)
    html.Div(id="fc-error-msg", style={"color":"#EF4444", "padding":"10px", "display":"none"}),

    # Visitor Forecast
    html.Div(className="chart-card", id="fc-vis-container", children=[
        html.Div(className="chart-card-header", children=[html.Span("Visitor Volume Forecast", className="chart-card-title")]),
        dcc.Graph(id="fc-visitor-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
    ]),

    # Revenue Forecast
    html.Div(className="chart-card", id="fc-rev-container", children=[
        html.Div(className="chart-card-header", children=[html.Span("Revenue Forecast", className="chart-card-title")]),
        dcc.Graph(id="fc-revenue-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
    ]),

    # Sub charts
    html.Div(className="chart-grid", id="fc-sub-container", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Historical YoY Growth", className="chart-card-title")]),
            dcc.Graph(id="fc-growth-chart", config=GRAPH_CONFIG, style={"height": "350px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Average Seasonal Pattern", className="chart-card-title")]),
            dcc.Graph(id="fc-seasonal-chart", config=GRAPH_CONFIG, style={"height": "350px"}),
        ]),
    ]),

    # Methodology
    html.Div(className="chart-card", children=[
        html.Div(className="chart-card-header", children=[html.Span("Model Methodology", className="chart-card-title")]),
        html.P("This forecast utilizes a linear trend progression built upon historical moving averages. "
               "The confidence band represents a ±15% variance from the projected mean, accounting for standard seasonal volatility. "
               "It is calculated dynamically using numpy polynomial fitting.", 
               style={"padding":"16px", "color":"#94A3B8"})
    ]),

    html.Div(className="chart-card", id="fc-insights"),
])

@dash.callback(
    [Output("fc-kpi-periods", "children"),
     Output("fc-kpi-proj-visitors", "children"),
     Output("fc-kpi-proj-revenue", "children"),
     Output("fc-kpi-trend", "children"),
     Output("fc-visitor-chart", "figure"),
     Output("fc-revenue-chart", "figure"),
     Output("fc-growth-chart", "figure"),
     Output("fc-seasonal-chart", "figure"),
     Output("fc-insights", "children"),
     Output("fc-error-msg", "children"),
     Output("fc-error-msg", "style")],
    [Input("fc-country-filter", "value"),
     Input("fc-type-filter", "value"),
     Input("fc-periods-slider", "value")],
    prevent_initial_call=False,
)
def update_forecast(countries, types, periods):
    f = {}
    if countries: f["countries"] = countries
    if types: f["tourist_types"] = types
    filters = f or None

    res = get_forecast_data(periods, filters)
    
    empty_fig = go.Figure().update_layout(**themed_layout(True))

    if "error" in res:
        return ("-", "-", "-", "-", empty_fig, empty_fig, empty_fig, empty_fig, "", 
                res["error"], {"color":"#EF4444", "padding":"10px", "display":"block"})
        
    hist = res["historical"]
    fc   = res["forecast"]

    # KPIs
    end_vis = fc["Visitors"].iloc[-1]
    end_rev = fc["Revenue"].iloc[-1]
    trend_dir = "Upward" if fc["Visitors"].iloc[-1] > fc["Visitors"].iloc[0] else "Downward"

    # Visitor Chart
    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=hist["YearMonth"], y=hist["Visitors"], name="Historical", line=dict(color="#6366F1", width=2)))
    # Confidence
    fig_v.add_trace(go.Scatter(
        x=list(fc["YearMonth"])+list(fc["YearMonth"][::-1]), 
        y=list(fc["Visitors_Hi"])+list(fc["Visitors_Lo"][::-1]), 
        fill="toself", fillcolor="rgba(249,115,22,0.15)", line=dict(width=0), name="Confidence Band"
    ))
    # FC line
    fig_v.add_trace(go.Scatter(x=fc["YearMonth"], y=fc["Visitors"], name="Forecast", line=dict(color="#F97316", width=2, dash="dash")))
    fig_v.add_vline(x=fc["YearMonth"].iloc[0], line_dash="dot", line_color="#64748B", annotation_text="Forecast Start")
    fig_v.update_layout(**themed_layout(True), yaxis_title="Visitors")

    # Revenue Chart
    fig_r = go.Figure()
    fig_r.add_trace(go.Scatter(x=hist["YearMonth"], y=hist["Revenue"], name="Historical", line=dict(color="#10B981", width=2)))
    fig_r.add_trace(go.Scatter(
        x=list(fc["YearMonth"])+list(fc["YearMonth"][::-1]), 
        y=list(fc["Revenue_Hi"])+list(fc["Revenue_Lo"][::-1]), 
        fill="toself", fillcolor="rgba(16,185,129,0.15)", line=dict(width=0), name="Confidence Band"
    ))
    fig_r.add_trace(go.Scatter(x=fc["YearMonth"], y=fc["Revenue"], name="Forecast", line=dict(color="#34D399", width=2, dash="dash")))
    fig_r.add_vline(x=fc["YearMonth"].iloc[0], line_dash="dot", line_color="#64748B")
    fig_r.update_layout(**themed_layout(True), yaxis_title="Revenue ($)")

    # Growth
    fig_g = go.Figure()
    yearly = hist.groupby("Year").agg({"Visitors":"sum"}).reset_index()
    yearly["Growth"] = yearly["Visitors"].pct_change() * 100
    if len(yearly) > 1:
        colors = ["#EF4444" if g < 0 else "#10B981" for g in yearly["Growth"]]
        fig_g.add_trace(go.Bar(x=yearly["Year"].astype(str), y=yearly["Growth"], marker_color=colors))
    fig_g.update_layout(**themed_layout(True), yaxis_title="YoY Growth %")

    # Seasonal
    fig_s = go.Figure()
    monthly_avg = hist.groupby("Month").agg({"Visitors":"mean"}).reset_index()
    MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    fig_s.add_trace(go.Bar(
        x=[MONTHS[int(m)-1] for m in monthly_avg["Month"]], 
        y=monthly_avg["Visitors"], marker_color="#8B5CF6"
    ))
    fig_s.update_layout(**themed_layout(True), yaxis_title="Avg Visitors")

    insights = html.Div([
        html.Div(className="chart-card-header", children=[html.Span("💡 Forecast Insights", className="chart-card-title")]),
        html.Div(style={"display":"flex","flexWrap":"wrap","gap":"12px","padding":"16px"}, children=[
            html.Div(className="insight-item", children=[html.Span("🔮", className="insight-icon"), html.Span(f"Trend direction over next {periods} months is {trend_dir}.", className="insight-text")]),
        ]),
    ])

    return (
        f"{periods} Months",
        f"{end_vis/1e6:.2f}M" if end_vis >= 1e6 else f"{end_vis:,.0f}",
        f"${end_rev/1e6:.1f}M",
        trend_dir,
        fig_v, fig_r, fig_g, fig_s, insights,
        "", {"display":"none"}
    )
