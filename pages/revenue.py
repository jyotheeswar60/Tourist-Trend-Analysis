"""pages/revenue.py — Revenue Analytics."""
import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
from dash_iconify import DashIconify
from services.data_service import (
    get_revenue_by_country, get_revenue_by_type, get_revenue_by_channel,
    get_revenue_by_accommodation, get_monthly_revenue, get_yearly_summary, get_filter_options,
)
from utils.chart_themes import themed_layout, apply_empty_state_annotation, PRIMARY_COLORS, TYPE_COLORS
from utils.chart_config import GRAPH_CONFIG
import numpy as np

dash.register_page(__name__, path="/revenue", name="Revenue Analytics",
                   title="Tourism Analytics | Revenue Analytics", order=4)

_opts = get_filter_options()
YEAR_OPTS    = [{"label": str(y), "value": y} for y in _opts["years"]]
COUNTRY_OPTS = [{"label": c, "value": c} for c in _opts["countries"]]
TYPE_OPTS    = [{"label": t, "value": t} for t in _opts["tourist_types"]]
MONTH_NAMES  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


layout = html.Div(className="page-enter", children=[
    html.Div(className="page-header", children=[
        html.Div(className="page-header-top", children=[
            html.Div([
                html.H1("Revenue Analytics", className="page-title"),
                html.P("Financial performance and spending behavior", className="page-subtitle"),
            ]),
        ]),
    ]),

    # Filters
    html.Div(className="filter-panel", children=[
        html.Div(className="filter-row", children=[
            html.Div(className="filter-group", children=[
                html.Label("Year", className="filter-label"),
                dcc.Dropdown(id="rev-year-filter", options=YEAR_OPTS, multi=True, placeholder="All Years", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Country", className="filter-label"),
                dcc.Dropdown(id="rev-country-filter", options=COUNTRY_OPTS, multi=True, placeholder="All Countries", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Tourist Type", className="filter-label"),
                dcc.Dropdown(id="rev-type-filter", options=TYPE_OPTS, multi=True, placeholder="All Types", className="filter-dropdown"),
            ]),
        ]),
    ]),

    # KPI Row
    html.Div(className="kpi-grid", style={"gridTemplateColumns":"repeat(5,1fr)"}, children=[
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Total Revenue", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:dollar-sign", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="rev-kpi-total"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Avg Spend / Visitor", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:credit-card", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="rev-kpi-avg-spend"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Top Country", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:trophy", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="rev-kpi-top-country"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Revenue Growth YoY", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:trending-up", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="rev-kpi-growth"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Best Month", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:calendar-star", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="rev-kpi-best-month"),
        ]),
    ]),

    # Full width Monthly
    html.Div(className="chart-card", children=[
        html.Div(className="chart-card-header", children=[html.Span("Monthly Revenue", className="chart-card-title")]),
        dcc.Loading(
            dcc.Graph(id="rev-monthly-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
            type="circle", color="#6366F1"
        ),
    ]),

    # Country + Type
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Revenue by Country (Top 15)", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(id="rev-country-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
                type="circle", color="#6366F1"
            ),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Revenue by Tourist Type", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(id="rev-type-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
                type="circle", color="#6366F1"
            ),
        ]),
    ]),

    # Channel + Accom
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Revenue by Booking Channel", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(id="rev-channel-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
                type="circle", color="#6366F1"
            ),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Revenue by Accommodation", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(id="rev-accom-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
                type="circle", color="#6366F1"
            ),
        ]),
    ]),

    # Scatter
    html.Div(className="chart-card", children=[
        html.Div(className="chart-card-header", children=[html.Span("Visitors vs Revenue by Country", className="chart-card-title")]),
        dcc.Loading(
            dcc.Graph(id="rev-scatter", config=GRAPH_CONFIG, style={"height": "400px"}),
            type="circle", color="#6366F1"
        ),
    ]),

    # Insights
    html.Div(className="chart-card", id="rev-insights"),
])

@dash.callback(
    [Output("rev-kpi-total", "children"),
     Output("rev-kpi-avg-spend", "children"),
     Output("rev-kpi-top-country", "children"),
     Output("rev-kpi-growth", "children"),
     Output("rev-kpi-best-month", "children"),
     Output("rev-monthly-chart", "figure"),
     Output("rev-country-chart", "figure"),
     Output("rev-type-chart", "figure"),
     Output("rev-channel-chart", "figure"),
     Output("rev-accom-chart", "figure"),
     Output("rev-scatter", "figure"),
     Output("rev-insights", "children")],
    [Input("rev-year-filter", "value"),
     Input("rev-country-filter", "value"),
     Input("rev-type-filter", "value")],
    prevent_initial_call=False,
)
def update_revenue(years, countries, types):
    f = {}
    if years: f["years"] = years
    if countries: f["countries"] = countries
    if types: f["tourist_types"] = types
    filters = f or None

    monthly_rev = get_monthly_revenue(filters)
    country_rev = get_revenue_by_country(filters)
    type_rev    = get_revenue_by_type(filters)
    channel_rev = get_revenue_by_channel(filters)
    accom_rev   = get_revenue_by_accommodation(filters)
    yearly      = get_yearly_summary(filters)

    total_rev = monthly_rev["Revenue"].sum() if not monthly_rev.empty else 0
    total_vis = monthly_rev["Visitors"].sum() if not monthly_rev.empty else 0
    avg_spend = total_rev / total_vis if total_vis > 0 else 0
    top_country = country_rev.iloc[0]["Country"] if not country_rev.empty else "N/A"
    
    yoy = 0.0
    if not yearly.empty and len(yearly) >= 2:
        curr = yearly.iloc[-1]["Revenue"]
        prev = yearly.iloc[-2]["Revenue"]
        yoy = (curr - prev) / prev * 100 if prev else 0

    best_month = "N/A"
    if not monthly_rev.empty:
        pm = monthly_rev.groupby("Month")["Revenue"].sum().idxmax()
        best_month = MONTH_NAMES[pm - 1]

    # Monthly Area
    fig_monthly = go.Figure()
    if monthly_rev.empty:
        apply_empty_state_annotation(fig_monthly)
    else:
        grp = monthly_rev.groupby(["Year", "Month"])["Revenue"].sum().reset_index().sort_values(["Year", "Month"])
        grp["Period"] = range(len(grp))
        grp["Label"] = grp.apply(lambda r: f"{MONTH_NAMES[int(r['Month'])-1]} {int(r['Year'])}", axis=1)
        fig_monthly.add_trace(go.Scatter(
            x=grp["Label"], y=grp["Revenue"], name="Revenue",
            mode="lines", line=dict(color="#10B981", width=2),
            fill="tozeroy", fillcolor="rgba(16,185,129,0.15)",
        ))
        fig_monthly.update_layout(**themed_layout(True))
        fig_monthly.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)", xaxis=dict(tickangle=-45))

    # Country Bar
    fig_country = go.Figure()
    if country_rev.empty:
        apply_empty_state_annotation(fig_country)
    else:
        top_c = country_rev.sort_values("Revenue", ascending=True)
        fig_country.add_trace(go.Bar(
            y=top_c["Country"], x=top_c["Revenue"], orientation="h",
            marker=dict(color=top_c["Revenue"], colorscale="Greens")
        ))
        fig_country.update_layout(**themed_layout(True))

    # Type Donut
    fig_type = go.Figure()
    if type_rev.empty:
        apply_empty_state_annotation(fig_type)
    else:
        fig_type.add_trace(go.Pie(
            labels=type_rev["Tourist_Type"], values=type_rev["Revenue"], hole=0.5,
            marker=dict(colors=[TYPE_COLORS.get(t, "#10B981") for t in type_rev["Tourist_Type"]])
        ))
        fig_type.update_layout(**themed_layout(True))

    # Channel Bar
    fig_channel = go.Figure()
    if channel_rev.empty:
        apply_empty_state_annotation(fig_channel)
    else:
        chan_srt = channel_rev.sort_values("Revenue", ascending=False)
        fig_channel.add_trace(go.Bar(
            x=chan_srt["Booking_Channel"], y=chan_srt["Revenue"], marker_color="#3B82F6"
        ))
        fig_channel.update_layout(**themed_layout(True), xaxis_title="Booking Channel", yaxis_title="Revenue ($)")

    # Accom Bar + Line
    fig_accom = go.Figure()
    if accom_rev.empty:
        apply_empty_state_annotation(fig_accom)
    else:
        acc_srt = accom_rev.sort_values("Revenue", ascending=False)
        fig_accom.add_trace(go.Bar(
            x=acc_srt["Accommodation_Type"], y=acc_srt["Revenue"], marker_color="#8B5CF6", name="Revenue"
        ))
        fig_accom.add_trace(go.Scatter(
            x=acc_srt["Accommodation_Type"], y=acc_srt["AvgSpend"], mode="lines+markers",
            line=dict(color="#F59E0B", width=2), name="Avg Spend", yaxis="y2"
        ))
        fig_accom.update_layout(**themed_layout(True), yaxis2=dict(title="Avg Spend ($)", overlaying="y", side="right"))

    # Scatter
    fig_scatter = go.Figure()
    if country_rev.empty:
        apply_empty_state_annotation(fig_scatter)
    else:
        fig_scatter.add_trace(go.Scatter(
            x=country_rev["Visitors"], y=country_rev["Revenue"], mode="markers",
            marker=dict(size=12, color=country_rev["Revenue"], colorscale="Viridis", showscale=True),
            text=country_rev["Country"], hoverinfo="text+x+y"
        ))
        fig_scatter.update_layout(**themed_layout(True), xaxis_title="Visitors", yaxis_title="Revenue ($)")

    insights = html.Div([
        html.Div(className="chart-card-header", children=[html.Span("💡 Revenue Insights", className="chart-card-title")]),
        html.Div(style={"display":"flex","flexWrap":"wrap","gap":"12px","padding":"16px"}, children=[
            html.Div(className="insight-item", children=[html.Span("💰", className="insight-icon"), html.Span(f"Total Revenue: ${total_rev/1e9:.2f}B.", className="insight-text")]),
            html.Div(className="insight-item", children=[html.Span("💳", className="insight-icon"), html.Span(f"Avg Spend per Visitor: ${avg_spend:.2f}.", className="insight-text")]),
        ]),
    ])

    return (
        f"${total_rev/1e9:.2f}B" if total_rev >= 1e9 else f"${total_rev/1e6:.1f}M",
        f"${avg_spend:.0f}",
        top_country,
        html.Span(f"{yoy:+.1f}%", className="kpi-trend-up" if yoy >= 0 else "kpi-trend-down"),
        best_month,
        fig_monthly, fig_country, fig_type, fig_channel, fig_accom, fig_scatter, insights
    )
