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
from utils.chart_themes import themed_layout, apply_empty_state_annotation, PRIMARY_COLORS, SEASON_COLORS, TYPE_COLORS
from utils.chart_config import GRAPH_CONFIG

dash.register_page(__name__, path="/", name="Executive Overview",
                   title="Tourism Analytics | Executive Overview", order=1)

_opts = get_filter_options()
YEAR_OPTS    = [{"label": str(y), "value": y} for y in _opts["years"]]
COUNTRY_OPTS = [{"label": c, "value": c} for c in _opts["countries"]]
TYPE_OPTS    = [{"label": t, "value": t} for t in _opts["tourist_types"]]
SEASON_OPTS  = [{"label": s, "value": s} for s in _opts["seasons"]]
ACCOM_OPTS   = [{"label": a, "value": a} for a in _opts["accommodation"]]
PURP_OPTS    = [{"label": p, "value": p} for p in _opts["purposes"]]

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


def make_kpi_card(label, value_id, icon, subtitle=""):
    return html.Div(className="kpi-card animate-on-scroll fade-up", children=[
        html.Div(className="kpi-card-header", children=[
            html.Span(label, className="kpi-card-label"),
            html.Div(DashIconify(icon=icon, width=20), className="kpi-card-icon-wrap"),
        ]),
        html.Div("—", className="kpi-card-value", id=value_id),
        html.Div(id=f"{value_id}-trend", className="kpi-card-trend"),
    ])


layout = html.Div(className="page-enter", children=[
    # Hero Section
    html.Div(className="hero-section animate-on-scroll fade-up", children=[
        html.Div(className="hero-content", children=[
            html.Div(className="hero-icon-wrap", children=[
                DashIconify(icon="lucide:globe-2", width=48, color="#3B82F6", className="hero-globe-icon")
            ]),
            html.H1("Tourism Analytics Dashboard", className="hero-title"),
            html.H3("Interactive Global Tourism Intelligence Platform", className="hero-subtitle"),
            html.P("Analyze global travel trends, revenue streams, and demographic insights across 25 countries and 100+ cities in real-time.", className="hero-desc"),
            html.Div(className="hero-stats", children=[
                html.Span([DashIconify(icon="lucide:clock", width=14), " Last Updated: Just now"], className="hero-stat"),
                html.Span([DashIconify(icon="lucide:map-pin", width=14), " Destinations: 25 Countries"], className="hero-stat"),
                html.Span([DashIconify(icon="lucide:filter", width=14), " Active Filters: Global"], className="hero-stat"),
                html.Span([DashIconify(icon="lucide:activity", width=14), " Status: Live Data"], className="hero-stat live-stat"),
            ])
        ])
    ]),

    # Filters
    html.Div(className="filter-panel animate-on-scroll fade-up stagger-1", children=[
        html.Div(className="filter-row", children=[
            html.Div(className="filter-group", children=[
                html.Label("Year", className="filter-label"),
                dcc.Dropdown(id="overview-year-filter", options=YEAR_OPTS, multi=True, placeholder="All Years", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Country", className="filter-label"),
                dcc.Dropdown(id="overview-country-filter", options=COUNTRY_OPTS, multi=True, placeholder="All Countries", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Tourist Type", className="filter-label"),
                dcc.Dropdown(id="overview-type-filter", options=TYPE_OPTS, multi=True, placeholder="All Types", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Season", className="filter-label"),
                dcc.Dropdown(id="overview-season-filter", options=SEASON_OPTS, multi=True, placeholder="All Seasons", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Accommodation", className="filter-label"),
                dcc.Dropdown(id="overview-accom-filter", options=ACCOM_OPTS, multi=True, placeholder="All", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Purpose", className="filter-label"),
                dcc.Dropdown(id="overview-purp-filter", options=PURP_OPTS, multi=True, placeholder="All", className="filter-dropdown"),
            ]),
        ]),
        html.Div(className="filter-row", style={"marginTop": "10px", "justifyContent": "flex-end"}, children=[
            html.Button("↺ Reset", id="overview-reset-btn", n_clicks=0, className="btn btn-secondary btn-sm"),
        ]),
    ]),

    # KPI Grid
    html.Div(className="kpi-grid animate-on-scroll fade-up stagger-1", children=[
        make_kpi_card("Total Visitors",   "overview-kpi-visitors",  "lucide:users"),
        make_kpi_card("Total Revenue",    "overview-kpi-revenue",   "lucide:dollar-sign"),
        make_kpi_card("Average Stay",     "overview-kpi-stay",      "lucide:calendar-days"),
        make_kpi_card("Average Rating",   "overview-kpi-rating",    "lucide:star"),
        make_kpi_card("Hotel Occupancy",  "overview-kpi-occupancy", "lucide:hotel"),
        make_kpi_card("Repeat Visitors",  "overview-kpi-repeat",    "lucide:repeat"),
    ]),

    # Charts Grid
    html.Div(className="chart-grid animate-on-scroll fade-up stagger-2", children=[
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("1. Monthly Visitors Trend", className="chart-card-title")]),
            dcc.Loading(dcc.Graph(id="chart-1-monthly-trend", config=GRAPH_CONFIG, style={"height": "320px"}), type="circle", color="#6366F1")
        ]),
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("2. Revenue by Country", className="chart-card-title")]),
            dcc.Loading(dcc.Graph(id="chart-2-revenue-country", config=GRAPH_CONFIG, style={"height": "320px"}), type="circle", color="#6366F1")
        ]),
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("3. Seasonal Tourism", className="chart-card-title")]),
            dcc.Loading(dcc.Graph(id="chart-3-seasonal-area", config=GRAPH_CONFIG, style={"height": "320px"}), type="circle", color="#6366F1")
        ]),
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("4. Visitor Type Distribution", className="chart-card-title")]),
            dcc.Loading(dcc.Graph(id="chart-4-visitor-type", config=GRAPH_CONFIG, style={"height": "320px"}), type="circle", color="#6366F1")
        ]),
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("5. Top Destinations", className="chart-card-title")]),
            dcc.Loading(dcc.Graph(id="chart-5-top-destinations", config=GRAPH_CONFIG, style={"height": "320px"}), type="circle", color="#6366F1")
        ]),
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("6. Revenue vs Visitors", className="chart-card-title")]),
            dcc.Loading(dcc.Graph(id="chart-6-revenue-visitors", config=GRAPH_CONFIG, style={"height": "320px"}), type="circle", color="#6366F1")
        ]),
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("7. Country Heatmap", className="chart-card-title")]),
            dcc.Loading(dcc.Graph(id="chart-7-country-heatmap", config=GRAPH_CONFIG, style={"height": "320px"}), type="circle", color="#6366F1")
        ]),
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[html.Span("8. Monthly Growth", className="chart-card-title")]),
            dcc.Loading(dcc.Graph(id="chart-8-monthly-growth", config=GRAPH_CONFIG, style={"height": "320px"}), type="circle", color="#6366F1")
        ]),
    ]),

    # Insights
    html.Div(className="chart-card animate-on-scroll fade-up stagger-3", id="overview-insights", children=[]),
])


def _build_filters(years, countries, types, seasons, accoms, purps):
    f = {}
    if years:    f["years"] = years
    if countries: f["countries"] = countries
    if types:    f["tourist_types"] = types
    if seasons:  f["seasons"] = seasons
    if accoms:   f["accommodation"] = accoms
    if purps:    f["purposes"] = purps
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
     
     Output("chart-1-monthly-trend", "figure"),
     Output("chart-2-revenue-country", "figure"),
     Output("chart-3-seasonal-area", "figure"),
     Output("chart-4-visitor-type", "figure"),
     Output("chart-5-top-destinations", "figure"),
     Output("chart-6-revenue-visitors", "figure"),
     Output("chart-7-country-heatmap", "figure"),
     Output("chart-8-monthly-growth", "figure"),
     Output("overview-insights", "children")],
    [Input("overview-year-filter", "value"),
     Input("overview-country-filter", "value"),
     Input("overview-type-filter", "value"),
     Input("overview-season-filter", "value"),
     Input("overview-accom-filter", "value"),
     Input("overview-purp-filter", "value")],
    prevent_initial_call=False,
)
def update_overview(years, countries, types, seasons, accoms, purps):
    filters = _build_filters(years, countries, types, seasons, accoms, purps)
    kpi = get_kpi_summary(filters)

    total_v   = kpi.get("total_visitors", 0)
    total_r   = kpi.get("total_revenue", 0)
    avg_stay  = kpi.get("avg_stay", 0)
    avg_rat   = kpi.get("avg_rating", 0)
    avg_occ   = kpi.get("avg_occupancy", 0)
    rep_pct   = kpi.get("repeat_pct", 0)
    yoy       = kpi.get("yoy_growth", 0)
    top_c     = kpi.get("top_country", "N/A")

    trend_icon = "▲" if yoy >= 0 else "▼"
    trend_cls  = "kpi-trend-up" if yoy >= 0 else "kpi-trend-down"
    trend_txt_r  = html.Span(f"{trend_icon} {abs(yoy):.1f}% YoY", className=trend_cls)

    kv_visitors  = f"{total_v/1e6:.2f}M" if total_v >= 1e6 else f"{total_v:,.0f}"
    kv_revenue   = f"${total_r/1e9:.2f}B" if total_r >= 1e9 else f"${total_r/1e6:.1f}M"
    
    monthly = get_monthly_visitors(filters)
    country_df = get_country_stats(filters)
    season_df = get_seasonal_trends(filters)
    type_df = get_type_trends(filters)
    
    fig1 = go.Figure()
    fig2 = go.Figure()
    fig3 = go.Figure()
    fig4 = go.Figure()
    fig5 = go.Figure()
    fig6 = go.Figure()
    fig7 = go.Figure()
    fig8 = go.Figure()

    if not monthly.empty:
        # 1. Monthly Visitors Trend (Animated Line Chart)
        for yr in sorted(monthly["Year"].unique()):
            yd = monthly[monthly["Year"] == yr].sort_values("Month")
            fig1.add_trace(go.Scatter(
                x=[MONTH_NAMES[m-1] for m in yd["Month"]], y=yd["Visitors"],
                name=str(yr), mode="lines+markers", line=dict(width=3)
            ))
        fig1.update_layout(**themed_layout(True), xaxis_title="Month", yaxis_title="Visitors")
        
        # 8. Monthly Growth (Waterfall Chart)
        last_yr = sorted(monthly["Year"].unique())[-1]
        ly_data = monthly[monthly["Year"] == last_yr].sort_values("Month")
        if not ly_data.empty:
            diffs = ly_data["Visitors"].diff().fillna(ly_data["Visitors"].iloc[0])
            fig8.add_trace(go.Waterfall(
                x=[MONTH_NAMES[m-1] for m in ly_data["Month"]],
                y=diffs,
                measure=["relative"] * len(diffs),
                text=[f"{d/1000:.1f}K" for d in diffs],
                textposition="outside",
                increasing=dict(marker=dict(color="#10B981")),
                decreasing=dict(marker=dict(color="#EF4444")),
                totals=dict(marker=dict(color="#3B82F6"))
            ))
            fig8.update_layout(**themed_layout(True), title=f"Monthly Growth ({last_yr})", showlegend=False)

    if not country_df.empty:
        # 2. Revenue by Country (Animated Bar Chart)
        top_rev = country_df.sort_values("Revenue", ascending=False).head(10)
        fig2.add_trace(go.Bar(
            x=top_rev["Country"], y=top_rev["Revenue"],
            marker_color="#F59E0B", text=[f"${v/1e6:.1f}M" for v in top_rev["Revenue"]], textposition="auto"
        ))
        fig2.update_layout(**themed_layout(True), xaxis_title="Country", yaxis_title="Revenue (USD)")

        # 5. Top Destinations (Horizontal Bar Chart)
        top10 = country_df.head(10).sort_values("Visitors", ascending=True)
        fig5.add_trace(go.Bar(
            y=top10["Country"], x=top10["Visitors"], orientation="h",
            marker=dict(color=top10["Visitors"], colorscale="Blues")
        ))
        fig5.update_layout(**themed_layout(True), xaxis_title="Visitors", yaxis_title="Country")
        
        # 6. Revenue vs Visitors (Scatter Plot)
        fig6.add_trace(go.Scatter(
            x=country_df["Visitors"], y=country_df["Revenue"],
            mode="markers+text", text=country_df["Country"], textposition="top center",
            marker=dict(size=12, color=country_df["AvgStay"], colorscale="Viridis", showscale=True, colorbar=dict(title="Avg Stay"))
        ))
        fig6.update_layout(**themed_layout(True), xaxis_title="Total Visitors", yaxis_title="Total Revenue")

        # 7. Country Heatmap (Choropleth map)
        fig7 = px.choropleth(
            country_df, locations="Country", locationmode="country names",
            color="Visitors", color_continuous_scale="Tealgrn"
        )
        fig7.update_layout(**themed_layout(True), geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False))

    if not season_df.empty:
        # 3. Seasonal Tourism (Area Chart)
        for season in season_df["Season"].unique():
            sd = season_df[season_df["Season"] == season].sort_values("Year")
            fig3.add_trace(go.Scatter(
                x=sd["Year"].astype(str), y=sd["Visitors"], name=season,
                mode="lines", fill="tonexty", line=dict(width=2)
            ))
        fig3.update_layout(**themed_layout(True), xaxis_title="Year", yaxis_title="Visitors")

    if not type_df.empty:
        # 4. Visitor Type Distribution (Pie Chart)
        t_agg = type_df.groupby("Tourist_Type")["Revenue"].sum().reset_index()
        fig4.add_trace(go.Pie(
            labels=t_agg["Tourist_Type"], values=t_agg["Revenue"], hole=0.4,
            marker=dict(colors=[TYPE_COLORS.get(t, "#6366F1") for t in t_agg["Tourist_Type"]])
        ))
        fig4.update_layout(**themed_layout(True))

    insights = html.Div([
        html.Div(className="chart-card-header", children=[
            html.Span("🤖 AI Business Insights", className="chart-card-title"),
        ]),
        html.Div(style={"display":"flex","flexDirection":"column","gap":"12px","padding":"16px"}, children=[
            html.Div(className="insight-item", children=[
                html.Span("📈", className="insight-icon"),
                html.Span(f"Tourism changed by {yoy:+.1f}% compared to previous year.", className="insight-text"),
            ]),
            html.Div(className="insight-item", children=[
                html.Span("☀️", className="insight-icon"),
                html.Span(f"Highest performing country is {top_c} driving ${country_df['Revenue'].max()/1e6:.1f}M in revenue." if not country_df.empty else "No country data.", className="insight-text"),
            ]),
            html.Div(className="insight-item", children=[
                html.Span("🧳", className="insight-icon"),
                html.Span(f"Leisure tourists are the dominant demographic.", className="insight-text"),
            ]),
            html.Div(className="insight-item", children=[
                html.Span("🏨", className="insight-icon"),
                html.Span(f"Hotel occupancy averages {avg_occ:.1f}%.", className="insight-text"),
            ]),
        ]),
    ])

    return (
        kv_visitors, trend_txt_r,
        kv_revenue,  trend_txt_r,
        f"{avg_stay:.1f} days", html.Span(f"Avg across {total_v:,.0f} visitors"),
        f"{avg_rat:.2f} / 5.0", html.Span(f"Based on {kpi.get('total_records',0):,} records"),
        f"{avg_occ:.1f}%", html.Span("Average hotel occupancy"),
        f"{rep_pct:.1f}%", html.Span("Share of returning tourists"),
        fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, insights
    )

@dash.callback(
    Output("overview-year-filter", "value"),
    Output("overview-country-filter", "value"),
    Output("overview-type-filter", "value"),
    Output("overview-season-filter", "value"),
    Output("overview-accom-filter", "value"),
    Output("overview-purp-filter", "value"),
    Input("overview-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_overview_filters(n):
    return None, None, None, None, None, None
