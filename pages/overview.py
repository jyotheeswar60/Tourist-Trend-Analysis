"""pages/overview.py — Executive Overview Dashboard."""
import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from dash_iconify import DashIconify
from services.data_service import (
    get_kpi_summary, get_monthly_visitors, get_yearly_summary,
    get_country_stats, get_seasonal_trends, get_type_trends, get_filter_options,
)
from utils.chart_themes import themed_layout, PRIMARY_COLORS, SEASON_COLORS, TYPE_COLORS
from utils.chart_config import GRAPH_CONFIG

dash.register_page(__name__, path="/", name="Executive Overview",
                   title="Tourism Analytics | Executive Overview", order=1)

_opts = get_filter_options()
YEAR_OPTS    = [{"label": str(y), "value": y} for y in _opts["years"]]
COUNTRY_OPTS = [{"label": c, "value": c} for c in _opts["countries"]]
TYPE_OPTS    = [{"label": t, "value": t} for t in _opts["tourist_types"]]

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


def make_kpi_card(label, value_id, icon, subtitle=""):
    return html.Div(className="kpi-card", children=[
        html.Div(className="kpi-card-header", children=[
            html.Span(label, className="kpi-card-label"),
            html.Div(DashIconify(icon=icon, width=20), className="kpi-card-icon-wrap"),
        ]),
        html.Div("—", className="kpi-card-value", id=value_id),
        html.Div(id=f"{value_id}-trend", className="kpi-card-trend"),
    ])


layout = html.Div(className="page-enter", children=[
    # Header
    html.Div(className="page-header", children=[
        html.Div(className="page-header-top", children=[
            html.Div([
                html.H1("Executive Overview", className="page-title"),
                html.P("Real-time KPIs and performance summary across all destinations · 2020–2025",
                       className="page-subtitle"),
            ]),
        ]),
    ]),

    # Filters
    html.Div(className="filter-panel", children=[
        html.Div(className="filter-row", children=[
            html.Div(className="filter-group", children=[
                html.Label("Year", className="filter-label"),
                dcc.Dropdown(id="overview-year-filter", options=YEAR_OPTS, multi=True,
                             placeholder="All Years", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Country", className="filter-label"),
                dcc.Dropdown(id="overview-country-filter", options=COUNTRY_OPTS, multi=True,
                             placeholder="All Countries", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Tourist Type", className="filter-label"),
                dcc.Dropdown(id="overview-type-filter", options=TYPE_OPTS, multi=True,
                             placeholder="All Types", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", style={"alignSelf": "flex-end"}, children=[
                html.Button("↺ Reset", id="overview-reset-btn", n_clicks=0,
                            className="btn btn-secondary btn-sm"),
            ]),
        ]),
    ]),

    # KPI Grid
    html.Div(className="kpi-grid", children=[
        make_kpi_card("Total Visitors",   "overview-kpi-visitors",  "lucide:users"),
        make_kpi_card("Total Revenue",    "overview-kpi-revenue",   "lucide:dollar-sign"),
        make_kpi_card("Avg Stay (Days)",  "overview-kpi-stay",      "lucide:calendar-days"),
        make_kpi_card("Avg Rating",       "overview-kpi-rating",    "lucide:star"),
        make_kpi_card("Hotel Occupancy",  "overview-kpi-occupancy", "lucide:hotel"),
        make_kpi_card("Repeat Visitors",  "overview-kpi-repeat",    "lucide:repeat"),
    ]),

    # Row 1: Monthly + Yearly
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[
                html.Span("Monthly Visitor Arrivals", className="chart-card-title"),
            ]),
            dcc.Graph(id="overview-monthly-chart", config=GRAPH_CONFIG, style={"height": "360px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[
                html.Span("Yearly Performance", className="chart-card-title"),
            ]),
            dcc.Graph(id="overview-yearly-chart", config=GRAPH_CONFIG, style={"height": "360px"}),
        ]),
    ]),

    # Row 2: Country + Type + Season
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1.4"}, children=[
            html.Div(className="chart-card-header", children=[
                html.Span("Top Countries by Visitors", className="chart-card-title"),
            ]),
            dcc.Graph(id="overview-country-chart", config=GRAPH_CONFIG, style={"height": "360px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[
                html.Span("Tourist Type Mix", className="chart-card-title"),
            ]),
            dcc.Graph(id="overview-type-chart", config=GRAPH_CONFIG, style={"height": "360px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[
                html.Span("Seasonal Distribution", className="chart-card-title"),
            ]),
            dcc.Graph(id="overview-season-chart", config=GRAPH_CONFIG, style={"height": "360px"}),
        ]),
    ]),

    # Insights
    html.Div(className="chart-card", id="overview-insights", children=[]),
])


def _build_filters(years, countries, types):
    f = {}
    if years:    f["years"] = years
    if countries: f["countries"] = countries
    if types:    f["tourist_types"] = types
    return f or None


@dash.callback(
    [Output("overview-kpi-visitors", "children"),
     Output("overview-kpi-visitors-trend", "children"),
     Output("overview-kpi-revenue", "children"),
     Output("overview-kpi-revenue-trend", "children"),
     Output("overview-kpi-stay", "children"),
     Output("overview-kpi-stay-trend", "children"),
     Output("overview-kpi-rating", "children"),
     Output("overview-kpi-rating-trend", "children"),
     Output("overview-kpi-occupancy", "children"),
     Output("overview-kpi-occupancy-trend", "children"),
     Output("overview-kpi-repeat", "children"),
     Output("overview-kpi-repeat-trend", "children"),
     Output("overview-monthly-chart", "figure"),
     Output("overview-yearly-chart", "figure"),
     Output("overview-country-chart", "figure"),
     Output("overview-type-chart", "figure"),
     Output("overview-season-chart", "figure"),
     Output("overview-insights", "children")],
    [Input("overview-year-filter", "value"),
     Input("overview-country-filter", "value"),
     Input("overview-type-filter", "value")],
    prevent_initial_call=False,
)
def update_overview(years, countries, types):
    filters = _build_filters(years, countries, types)
    kpi = get_kpi_summary(filters)

    # KPI values
    total_v   = kpi.get("total_visitors", 0)
    total_r   = kpi.get("total_revenue", 0)
    avg_stay  = kpi.get("avg_stay", 0)
    avg_rat   = kpi.get("avg_rating", 0)
    avg_occ   = kpi.get("avg_occupancy", 0)
    rep_pct   = kpi.get("repeat_pct", 0)
    yoy       = kpi.get("yoy_growth", 0)
    top_c     = kpi.get("top_country", "N/A")
    top_city  = kpi.get("top_city", "N/A")

    trend_icon = "▲" if yoy >= 0 else "▼"
    trend_cls  = "kpi-trend-up" if yoy >= 0 else "kpi-trend-down"
    trend_txt  = f"{trend_icon} {abs(yoy):.1f}% YoY"

    kv_visitors  = f"{total_v/1e6:.2f}M" if total_v >= 1e6 else f"{total_v:,.0f}"
    kv_revenue   = f"${total_r/1e9:.2f}B" if total_r >= 1e9 else f"${total_r/1e6:.1f}M"
    kv_stay      = f"{avg_stay:.1f} days"
    kv_rating    = f"{avg_rat:.2f} / 5.0"
    kv_occupancy = f"{avg_occ:.1f}%"
    kv_repeat    = f"{rep_pct:.1f}%"

    trend_txt_r = html.Span(trend_txt, className=trend_cls)

    # ── Monthly Chart ────────────────────────────────────────────────────
    monthly = get_monthly_visitors(filters)
    fig_monthly = go.Figure()
    years_in = sorted(monthly["Year"].unique()) if not monthly.empty else []
    colors = PRIMARY_COLORS
    for i, yr in enumerate(years_in):
        yd = monthly[monthly["Year"] == yr].sort_values("Month")
        fig_monthly.add_trace(go.Scatter(
            x=[MONTH_NAMES[m-1] for m in yd["Month"]],
            y=yd["Visitors"],
            name=str(yr),
            mode="lines+markers",
            line=dict(color=colors[i % len(colors)], width=2),
            fill="tozeroy" if len(years_in) == 1 else "none",
            fillcolor=f"rgba(99,102,241,0.08)",
        ))
    fig_monthly.update_layout(**themed_layout(True), title="Monthly Visitor Arrivals",
                               xaxis_title="Month", yaxis_title="Visitors")

    # ── Yearly Chart ─────────────────────────────────────────────────────
    yearly = get_yearly_summary(filters)
    fig_yearly = go.Figure()
    if not yearly.empty:
        fig_yearly.add_trace(go.Bar(
            x=yearly["Year"].astype(str), y=yearly["Visitors"],
            name="Visitors", marker_color="#6366F1", yaxis="y"
        ))
        fig_yearly.add_trace(go.Scatter(
            x=yearly["Year"].astype(str), y=yearly["Revenue"],
            name="Revenue (USD)", line=dict(color="#10B981", width=2),
            mode="lines+markers", yaxis="y2"
        ))
        fig_yearly.update_layout(
            **themed_layout(True),
            title="Yearly Visitors & Revenue",
            yaxis=dict(title="Visitors"),
            yaxis2=dict(title="Revenue (USD)", overlaying="y", side="right"),
            barmode="group",
        )

    # ── Country Chart ────────────────────────────────────────────────────
    country = get_country_stats(filters).head(10)
    fig_country = go.Figure()
    if not country.empty:
        fig_country.add_trace(go.Bar(
            x=country["Visitors"], y=country["Country"],
            orientation="h",
            marker=dict(color=country["Visitors"], colorscale="Viridis"),
            text=[f"{v/1e3:.0f}K" for v in country["Visitors"]],
            textposition="outside",
        ))
    fig_country.update_layout(**themed_layout(True), title="Top 10 Countries",
                               xaxis_title="Total Visitors", yaxis=dict(autorange="reversed"))

    # ── Type Donut ───────────────────────────────────────────────────────
    type_df = get_type_trends(filters)
    type_agg = type_df.groupby("Tourist_Type")["Visitors"].sum().reset_index() if not type_df.empty else type_df
    fig_type = go.Figure()
    if not type_agg.empty:
        fig_type.add_trace(go.Pie(
            labels=type_agg["Tourist_Type"], values=type_agg["Visitors"],
            hole=0.5,
            marker=dict(colors=[TYPE_COLORS.get(t, "#6366F1") for t in type_agg["Tourist_Type"]]),
        ))
    fig_type.update_layout(**themed_layout(True), title="Tourist Types", showlegend=True)

    # ── Season Chart ─────────────────────────────────────────────────────
    season_df = get_seasonal_trends(filters)
    season_agg = season_df.groupby("Season")["Visitors"].sum().reset_index() if not season_df.empty else season_df
    fig_season = go.Figure()
    if not season_agg.empty:
        fig_season.add_trace(go.Pie(
            labels=season_agg["Season"], values=season_agg["Visitors"],
            hole=0.5,
            marker=dict(colors=[SEASON_COLORS.get(s, "#6366F1") for s in season_agg["Season"]]),
        ))
    fig_season.update_layout(**themed_layout(True), title="By Season")

    # ── Insights ─────────────────────────────────────────────────────────
    best_season = season_agg.loc[season_agg["Visitors"].idxmax(), "Season"] if not season_agg.empty else "N/A"
    top_type    = type_agg.loc[type_agg["Visitors"].idxmax(), "Tourist_Type"] if not type_agg.empty else "N/A"

    insights = html.Div([
        html.Div(className="chart-card-header", children=[
            html.Span("💡 Key Insights", className="chart-card-title"),
        ]),
        html.Div(style={"display":"flex","flexWrap":"wrap","gap":"12px","padding":"16px"}, children=[
            html.Div(className="insight-item", children=[
                html.Span("🏆", className="insight-icon"),
                html.Span(f"Top destination: {top_c} leads all countries by visitor volume.", className="insight-text"),
            ]),
            html.Div(className="insight-item", children=[
                html.Span("🏙️", className="insight-icon"),
                html.Span(f"Most visited city: {top_city}.", className="insight-text"),
            ]),
            html.Div(className="insight-item", children=[
                html.Span("📈", className="insight-icon"),
                html.Span(f"YoY visitor growth: {yoy:+.1f}% compared to previous year.", className="insight-text"),
            ]),
            html.Div(className="insight-item", children=[
                html.Span("🌤️", className="insight-icon"),
                html.Span(f"Peak season: {best_season} records the highest tourist volumes.", className="insight-text"),
            ]),
            html.Div(className="insight-item", children=[
                html.Span("🎯", className="insight-icon"),
                html.Span(f"Dominant tourist segment: {top_type} tourism drives most arrivals.", className="insight-text"),
            ]),
            html.Div(className="insight-item", children=[
                html.Span("🔁", className="insight-icon"),
                html.Span(f"{rep_pct:.1f}% of tourists are repeat visitors — strong destination loyalty.", className="insight-text"),
            ]),
        ]),
    ])

    return (
        kv_visitors, trend_txt_r,
        kv_revenue,  trend_txt_r,
        kv_stay,     html.Span(f"Avg across {total_v:,.0f} visitors"),
        kv_rating,   html.Span(f"Based on {kpi.get('total_records',0):,} records"),
        kv_occupancy, html.Span("Average hotel occupancy"),
        kv_repeat,   html.Span("Share of returning tourists"),
        fig_monthly, fig_yearly, fig_country, fig_type, fig_season, insights,
    )


@dash.callback(
    Output("overview-year-filter", "value"),
    Output("overview-country-filter", "value"),
    Output("overview-type-filter", "value"),
    Input("overview-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_overview_filters(n):
    return None, None, None
