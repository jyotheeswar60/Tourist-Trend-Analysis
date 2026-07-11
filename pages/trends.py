"""pages/trends.py — Tourism Trends Analysis."""
import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import numpy as np
from dash_iconify import DashIconify
from services.data_service import (
    get_monthly_visitors, get_yearly_summary, get_seasonal_trends,
    get_quarterly_trends, get_type_trends, get_moving_average, get_filter_options,
)
from utils.chart_themes import themed_layout, PRIMARY_COLORS, SEASON_COLORS, TYPE_COLORS
from utils.chart_config import GRAPH_CONFIG

dash.register_page(__name__, path="/trends", name="Tourism Trends",
                   title="Tourism Analytics | Tourism Trends", order=2)

_opts = get_filter_options()
YEAR_OPTS    = [{"label": str(y), "value": y} for y in _opts["years"]]
COUNTRY_OPTS = [{"label": c, "value": c} for c in _opts["countries"]]
TYPE_OPTS    = [{"label": t, "value": t} for t in _opts["tourist_types"]]
MONTH_NAMES  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


layout = html.Div(className="page-enter", children=[
    html.Div(className="page-header", children=[
        html.Div(className="page-header-top", children=[
            html.Div([
                html.H1("Tourism Trends", className="page-title"),
                html.P("Monthly, seasonal, and annual visitor trend analysis · 2020–2025", className="page-subtitle"),
            ]),
        ]),
    ]),

    # Filters
    html.Div(className="filter-panel", children=[
        html.Div(className="filter-row", children=[
            html.Div(className="filter-group", children=[
                html.Label("Year", className="filter-label"),
                dcc.Dropdown(id="trends-year-filter", options=YEAR_OPTS, multi=True,
                             placeholder="All Years", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Country", className="filter-label"),
                dcc.Dropdown(id="trends-country-filter", options=COUNTRY_OPTS, multi=True,
                             placeholder="All Countries", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Tourist Type", className="filter-label"),
                dcc.Dropdown(id="trends-type-filter", options=TYPE_OPTS, multi=True,
                             placeholder="All Types", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", style={"alignSelf": "flex-end"}, children=[
                html.Button("↺ Reset", id="trends-reset-btn", n_clicks=0,
                            className="btn btn-secondary btn-sm"),
            ]),
        ]),
    ]),

    # KPI Row
    html.Div(className="kpi-grid", style={"gridTemplateColumns":"repeat(4,1fr)"}, children=[
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Total Visitors", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:users", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="trends-kpi-total"),
            html.Div("Across all years", className="kpi-card-trend"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("YoY Growth", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:trending-up", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="trends-kpi-growth"),
            html.Div("Latest vs previous year", className="kpi-card-trend"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Peak Month", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:calendar", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="trends-kpi-peak-month"),
            html.Div("Highest visitor month", className="kpi-card-trend"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Best Season", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:sun", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="trends-kpi-best-season"),
            html.Div("Highest arrivals season", className="kpi-card-trend"),
        ]),
    ]),

    # Monthly with MA — full width
    html.Div(className="chart-card", children=[
        html.Div(className="chart-card-header", children=[html.Span("Monthly Arrivals + 3-Month Moving Average", className="chart-card-title")]),
        dcc.Graph(id="trends-monthly-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
    ]),

    # Yearly + Quarterly heatmap
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Yearly Visitor Comparison", className="chart-card-title")]),
            dcc.Graph(id="trends-yearly-chart", config=GRAPH_CONFIG, style={"height": "360px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Quarterly Heatmap", className="chart-card-title")]),
            dcc.Graph(id="trends-quarterly-chart", config=GRAPH_CONFIG, style={"height": "360px"}),
        ]),
    ]),

    # Seasonal + Type stacked area
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Seasonal Trends by Year", className="chart-card-title")]),
            dcc.Graph(id="trends-seasonal-chart", config=GRAPH_CONFIG, style={"height": "360px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Tourist Type Mix Over Time", className="chart-card-title")]),
            dcc.Graph(id="trends-type-chart", config=GRAPH_CONFIG, style={"height": "360px"}),
        ]),
    ]),

    # Insights
    html.Div(className="chart-card", id="trends-insights"),
])


@dash.callback(
    [Output("trends-kpi-total", "children"),
     Output("trends-kpi-growth", "children"),
     Output("trends-kpi-peak-month", "children"),
     Output("trends-kpi-best-season", "children"),
     Output("trends-monthly-chart", "figure"),
     Output("trends-yearly-chart", "figure"),
     Output("trends-quarterly-chart", "figure"),
     Output("trends-seasonal-chart", "figure"),
     Output("trends-type-chart", "figure"),
     Output("trends-insights", "children")],
    [Input("trends-year-filter", "value"),
     Input("trends-country-filter", "value"),
     Input("trends-type-filter", "value")],
    prevent_initial_call=False,
)
def update_trends(years, countries, types):
    f = {}
    if years:    f["years"] = years
    if countries: f["countries"] = countries
    if types:    f["tourist_types"] = types
    filters = f or None

    yearly   = get_yearly_summary(filters)
    monthly  = get_monthly_visitors(filters)
    seasonal = get_seasonal_trends(filters)
    quarterly = get_quarterly_trends(filters)
    type_df  = get_type_trends(filters)
    ma_df    = get_moving_average(3, filters)

    # KPIs
    total_v = int(monthly["Visitors"].sum()) if not monthly.empty else 0
    yoy = 0.0
    if not yearly.empty and len(yearly) >= 2:
        curr = yearly.iloc[-1]["Visitors"]
        prev = yearly.iloc[-2]["Visitors"]
        yoy = (curr - prev) / prev * 100 if prev else 0

    peak_month = "N/A"
    if not monthly.empty:
        pm = monthly.groupby("Month")["Visitors"].sum().idxmax()
        peak_month = MONTH_NAMES[pm - 1]

    best_season = "N/A"
    if not seasonal.empty:
        s = seasonal.groupby("Season")["Visitors"].sum()
        best_season = s.idxmax()

    # ── Monthly + MA chart ───────────────────────────────────────────────
    fig_monthly = go.Figure()
    if not monthly.empty:
        grp = monthly.groupby(["Year", "Month"])["Visitors"].sum().reset_index().sort_values(["Year", "Month"])
        grp["Period"] = range(len(grp))
        grp["Label"] = grp.apply(lambda r: f"{MONTH_NAMES[r['Month']-1]} {r['Year']}", axis=1)
        fig_monthly.add_trace(go.Scatter(
            x=grp["Label"], y=grp["Visitors"], name="Monthly Visitors",
            mode="lines", line=dict(color="#6366F1", width=1.5),
            fill="tozeroy", fillcolor="rgba(99,102,241,0.08)",
        ))
        # 3-month MA
        grp["MA3"] = grp["Visitors"].rolling(3, min_periods=1).mean()
        fig_monthly.add_trace(go.Scatter(
            x=grp["Label"], y=grp["MA3"], name="3-Month MA",
            mode="lines", line=dict(color="#F59E0B", width=2, dash="dash"),
        ))
    fig_monthly.update_layout(**themed_layout(True),
                               xaxis_title="Month", yaxis_title="Visitors",
                               xaxis=dict(tickangle=-45))

    # ── Yearly bar ───────────────────────────────────────────────────────
    fig_yearly = go.Figure()
    if not yearly.empty:
        colors_y = ["#EF4444" if g < 0 else "#10B981" for g in yearly["GrowthPct"].fillna(0)]
        fig_yearly.add_trace(go.Bar(x=yearly["Year"].astype(str), y=yearly["Visitors"],
                                     marker_color="#6366F1", name="Visitors"))
        for i, (_, row) in enumerate(yearly.iterrows()):
            if not np.isnan(row["GrowthPct"]):
                fig_yearly.add_annotation(
                    x=str(int(row["Year"])), y=row["Visitors"],
                    text=f"{row['GrowthPct']:+.1f}%", showarrow=False,
                    yshift=10, font=dict(color=colors_y[i], size=11)
                )
    fig_yearly.update_layout(**themed_layout(True), xaxis_title="Year", yaxis_title="Visitors")

    # ── Quarterly heatmap ────────────────────────────────────────────────
    fig_quarterly = go.Figure()
    if not quarterly.empty:
        pivot = quarterly.groupby(["Year", "Quarter"])["Visitors"].sum().unstack(fill_value=0)
        fig_quarterly.add_trace(go.Heatmap(
            z=pivot.values,
            x=[f"Q{q}" for q in pivot.columns],
            y=pivot.index.astype(str),
            colorscale="Viridis",
            text=[[f"{v:,.0f}" for v in row] for row in pivot.values],
            texttemplate="%{text}",
        ))
    fig_quarterly.update_layout(**themed_layout(True), xaxis_title="Quarter", yaxis_title="Year")

    # ── Seasonal grouped bar ─────────────────────────────────────────────
    fig_seasonal = go.Figure()
    if not seasonal.empty:
        season_order = ["Spring", "Summer", "Autumn", "Winter"]
        for season in season_order:
            sd = seasonal[seasonal["Season"] == season].sort_values("Year")
            if not sd.empty:
                fig_seasonal.add_trace(go.Bar(
                    x=sd["Year"].astype(str), y=sd["Visitors"], name=season,
                    marker_color=SEASON_COLORS.get(season, "#6366F1"),
                ))
    fig_seasonal.update_layout(**themed_layout(True), barmode="group",
                                xaxis_title="Year", yaxis_title="Visitors")

    # ── Tourist type stacked area ────────────────────────────────────────
    fig_type = go.Figure()
    if not type_df.empty:
        type_monthly = type_df.groupby(["Year", "Tourist_Type"])["Visitors"].sum().reset_index()
        for ttype in type_monthly["Tourist_Type"].unique():
            td = type_monthly[type_monthly["Tourist_Type"] == ttype].sort_values("Year")
            fig_type.add_trace(go.Scatter(
                x=td["Year"].astype(str), y=td["Visitors"], name=ttype,
                stackgroup="one",
                fillcolor=TYPE_COLORS.get(ttype, "#6366F1"),
                line=dict(color=TYPE_COLORS.get(ttype, "#6366F1")),
                mode="lines",
            ))
    fig_type.update_layout(**themed_layout(True), xaxis_title="Year", yaxis_title="Visitors")

    # Insights
    insights = html.Div([
        html.Div(className="chart-card-header", children=[html.Span("💡 Trend Insights", className="chart-card-title")]),
        html.Div(style={"display":"flex","flexWrap":"wrap","gap":"12px","padding":"16px"}, children=[
            html.Div(className="insight-item", children=[html.Span("📅", className="insight-icon"), html.Span(f"Peak month for arrivals: {peak_month}.", className="insight-text")]),
            html.Div(className="insight-item", children=[html.Span("🌤️", className="insight-icon"), html.Span(f"Best season: {best_season} consistently draws the most tourists.", className="insight-text")]),
            html.Div(className="insight-item", children=[html.Span("📈", className="insight-icon"), html.Span(f"Year-over-year growth: {yoy:+.1f}%.", className="insight-text")]),
            html.Div(className="insight-item", children=[html.Span("👥", className="insight-icon"), html.Span(f"Total visitors analysed: {total_v:,.0f}.", className="insight-text")]),
        ]),
    ])

    return (
        f"{total_v/1e6:.2f}M" if total_v >= 1e6 else f"{total_v:,.0f}",
        html.Span(f"{yoy:+.1f}%", className="kpi-trend-up" if yoy >= 0 else "kpi-trend-down"),
        peak_month, best_season,
        fig_monthly, fig_yearly, fig_quarterly, fig_seasonal, fig_type, insights,
    )


@dash.callback(
    Output("trends-year-filter", "value"),
    Output("trends-country-filter", "value"),
    Output("trends-type-filter", "value"),
    Input("trends-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_trends(n): return None, None, None
