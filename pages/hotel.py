"""pages/hotel.py — Hotel Analytics."""
import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from dash_iconify import DashIconify
from services.data_service import (
    get_occupancy_by_country, get_occupancy_trend, get_occupancy_by_season,
    get_accommodation_performance, get_by_accommodation, get_filter_options
)
from utils.chart_themes import themed_layout, apply_empty_state_annotation, PRIMARY_COLORS
from utils.chart_config import GRAPH_CONFIG

dash.register_page(__name__, path="/hotel", name="Hotel Analytics",
                   title="Tourism Analytics | Hotel Analytics", order=6)

_opts = get_filter_options()
YEAR_OPTS    = [{"label": str(y), "value": y} for y in _opts["years"]]
COUNTRY_OPTS = [{"label": c, "value": c} for c in _opts["countries"]]
SEASON_OPTS  = [{"label": s, "value": s} for s in _opts["seasons"]]
MONTH_NAMES  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

layout = html.Div(className="page-enter", children=[
    html.Div(className="page-header animate-on-scroll fade-up", children=[
        html.Div(className="page-header-top", children=[
            html.Div([
                html.H1("Hotel Analytics", className="page-title"),
                html.P("Occupancy rates, booking trends, and accommodation performance", className="page-subtitle"),
            ]),
        ]),
    ]),

    # Filters
    html.Div(className="filter-panel animate-on-scroll fade-up stagger-1", children=[
        html.Div(className="filter-row", children=[
            html.Div(className="filter-group", children=[
                html.Label("Year", className="filter-label"),
                dcc.Dropdown(id="hotel-year-filter", options=YEAR_OPTS, multi=True, placeholder="All Years", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Country", className="filter-label"),
                dcc.Dropdown(id="hotel-country-filter", options=COUNTRY_OPTS, multi=True, placeholder="All Countries", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Season", className="filter-label"),
                dcc.Dropdown(id="hotel-season-filter", options=SEASON_OPTS, multi=True, placeholder="All Seasons", className="filter-dropdown"),
            ]),
        ]),
    ]),

    # KPI Row
    html.Div(className="kpi-grid animate-on-scroll fade-up stagger-1", style={"gridTemplateColumns":"repeat(4,1fr)"}, children=[
        html.Div(className="kpi-card animate-on-scroll fade-up", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Avg Occupancy", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:hotel", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="hotel-kpi-avg-occ"),
        ]),
        html.Div(className="kpi-card animate-on-scroll fade-up", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Highest Occupancy (Country)", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:globe", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="hotel-kpi-top-country"),
        ]),
        html.Div(className="kpi-card animate-on-scroll fade-up", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Best Accom. Type", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:bed-double", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="hotel-kpi-best-accom"),
        ]),
        html.Div(className="kpi-card animate-on-scroll fade-up", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Peak Occupancy Month", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:calendar-check", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="hotel-kpi-peak-month"),
        ]),
    ]),

    # Trend
    html.Div(className="chart-card animate-on-scroll fade-up stagger-3", children=[
        html.Div(className="chart-card-header", children=[html.Span("Occupancy Trend", className="chart-card-title")]),
        dcc.Graph(id="hotel-trend-chart", config=GRAPH_CONFIG, style={"height": "380px"}),
    ]),

    # Country + Heatmap
    html.Div(className="chart-grid animate-on-scroll fade-up stagger-2", children=[
        html.Div(className="chart-card animate-on-scroll fade-up stagger-3", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Occupancy by Country (Top 15)", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(id="hotel-country-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
                type="circle", color="#6366F1"
            ),
        ]),
        html.Div(className="chart-card animate-on-scroll fade-up stagger-3", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Occupancy by Season & Accommodation", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(id="hotel-season-heat", config=GRAPH_CONFIG, style={"height": "400px"}),
                type="circle", color="#6366F1"
            ),
        ]),
    ]),

    # Accom Perf
    html.Div(className="chart-card animate-on-scroll fade-up stagger-3", children=[
        html.Div(className="chart-card-header", children=[html.Span("Accommodation Performance", className="chart-card-title")]),
        dcc.Loading(
            dcc.Graph(id="hotel-accom-chart", config=GRAPH_CONFIG, style={"height": "380px"}),
            type="circle", color="#6366F1"
        ),
    ]),

    # Scatter + Donut
    html.Div(className="chart-grid animate-on-scroll fade-up stagger-2", children=[
        html.Div(className="chart-card animate-on-scroll fade-up stagger-3", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Occupancy vs Revenue (by Country)", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(id="hotel-scatter", config=GRAPH_CONFIG, style={"height": "380px"}),
                type="circle", color="#6366F1"
            ),
        ]),
        html.Div(className="chart-card animate-on-scroll fade-up stagger-3", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Accommodation Revenue Share", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(id="hotel-accom-rev", config=GRAPH_CONFIG, style={"height": "380px"}),
                type="circle", color="#6366F1"
            ),
        ]),
    ]),

    # Insights
    html.Div(className="chart-card animate-on-scroll fade-up stagger-3", id="hotel-insights"),
])

@dash.callback(
    [Output("hotel-kpi-avg-occ", "children"),
     Output("hotel-kpi-top-country", "children"),
     Output("hotel-kpi-best-accom", "children"),
     Output("hotel-kpi-peak-month", "children"),
     Output("hotel-trend-chart", "figure"),
     Output("hotel-country-chart", "figure"),
     Output("hotel-season-heat", "figure"),
     Output("hotel-accom-chart", "figure"),
     Output("hotel-scatter", "figure"),
     Output("hotel-accom-rev", "figure"),
     Output("hotel-insights", "children")],
    [Input("hotel-year-filter", "value"),
     Input("hotel-country-filter", "value"),
     Input("hotel-season-filter", "value")],
    prevent_initial_call=False,
)
def update_hotel(years, countries, seasons):
    f = {}
    if years: f["years"] = years
    if countries: f["countries"] = countries
    if seasons: f["seasons"] = seasons
    filters = f or None

    occ_country = get_occupancy_by_country(filters)
    occ_trend   = get_occupancy_trend(filters)
    occ_season  = get_occupancy_by_season(filters)
    accom_perf  = get_accommodation_performance(filters)
    by_accom    = get_by_accommodation(filters)

    avg_occ = occ_country["AvgOccupancy"].mean() if not occ_country.empty else 0
    top_c   = occ_country.iloc[0]["Country"] if not occ_country.empty else "N/A"
    best_a  = accom_perf.iloc[0]["Accommodation_Type"] if not accom_perf.empty else "N/A"
    
    peak_m = "N/A"
    if not occ_trend.empty:
        om = occ_trend.groupby("Month")["AvgOccupancy"].mean().idxmax()
        peak_m = MONTH_NAMES[om-1]

    # Trend
    fig_trend = go.Figure()
    if occ_trend.empty:
        apply_empty_state_annotation(fig_trend)
    else:
        grp = occ_trend.copy()
        grp["Label"] = grp.apply(lambda r: f"{MONTH_NAMES[int(r['Month'])-1]} {int(r['Year'])}", axis=1)
        fig_trend.add_trace(go.Scatter(
            x=grp["Label"], y=grp["AvgOccupancy"], mode="lines+markers",
            line=dict(color="#F59E0B", width=2), fill="tozeroy", fillcolor="rgba(245,158,11,0.15)"
        ))
        fig_trend.update_layout(**themed_layout(True))
        fig_trend.update_layout(xaxis_title="Month", yaxis_title="Occupancy %", xaxis=dict(tickangle=-45))

    # Country
    fig_country = go.Figure()
    if occ_country.empty:
        apply_empty_state_annotation(fig_country)
    else:
        top15 = occ_country.head(15).sort_values("AvgOccupancy", ascending=True)
        fig_country.add_trace(go.Bar(
            y=top15["Country"], x=top15["AvgOccupancy"], orientation="h",
            marker=dict(color=top15["AvgOccupancy"], colorscale="Oranges")
        ))
        fig_country.update_layout(**themed_layout(True))

    # Heatmap
    fig_heat = go.Figure()
    if occ_season.empty:
        apply_empty_state_annotation(fig_heat)
    else:
        pivot = occ_season.pivot(index="Accommodation_Type", columns="Season", values="AvgOccupancy").fillna(0)
        fig_heat.add_trace(go.Heatmap(
            z=pivot.values, x=pivot.columns, y=pivot.index, colorscale="Oranges",
            text=pivot.values.round(1), texttemplate="%{text}%"
        ))
        fig_heat.update_layout(**themed_layout(True))

    # Accom Perf
    fig_perf = go.Figure()
    if accom_perf.empty:
        apply_empty_state_annotation(fig_perf)
    else:
        fig_perf.add_trace(go.Bar(
            x=accom_perf["Accommodation_Type"], y=accom_perf["AvgOccupancy"],
            name="Occupancy %", marker_color="#8B5CF6"
        ))
        fig_perf.add_trace(go.Scatter(
            x=accom_perf["Accommodation_Type"], y=accom_perf["AvgRating"]*20, # Scale rating 1-5 to 20-100 for visual
            name="Rating (scaled)", line=dict(color="#10B981", width=2), mode="lines+markers"
        ))
        fig_perf.update_layout(**themed_layout(True), barmode="group")

    # Scatter
    fig_scat = go.Figure()
    if occ_country.empty:
        apply_empty_state_annotation(fig_scat)
    else:
        fig_scat.add_trace(go.Scatter(
            x=occ_country["AvgOccupancy"], y=occ_country["Revenue"], mode="markers",
            marker=dict(size=occ_country["Visitors"]/occ_country["Visitors"].max()*50, color="#06B6D4", opacity=0.7),
            text=occ_country["Country"], hoverinfo="text+x+y"
        ))
        fig_scat.update_layout(**themed_layout(True), xaxis_title="Occupancy %", yaxis_title="Revenue ($)")

    # Donut
    fig_donut = go.Figure()
    if by_accom.empty:
        apply_empty_state_annotation(fig_donut)
    else:
        fig_donut.add_trace(go.Pie(
            labels=by_accom["Accommodation_Type"], values=by_accom["Revenue"], hole=0.5,
            marker=dict(colors=PRIMARY_COLORS)
        ))
        fig_donut.update_layout(**themed_layout(True))

    insights = html.Div([
        html.Div(className="chart-card-header", children=[html.Span("💡 Hotel Insights", className="chart-card-title")]),
        html.Div(style={"display":"flex","flexWrap":"wrap","gap":"12px","padding":"16px"}, children=[
            html.Div(className="insight-item", children=[html.Span("🏨", className="insight-icon"), html.Span(f"Average Occupancy: {avg_occ:.1f}%.", className="insight-text")]),
            html.Div(className="insight-item", children=[html.Span("📈", className="insight-icon"), html.Span(f"Peak Month: {peak_m}.", className="insight-text")]),
        ]),
    ])

    return (
        f"{avg_occ:.1f}%", top_c, best_a, peak_m,
        fig_trend, fig_country, fig_heat, fig_perf, fig_scat, fig_donut, insights
    )
