"""pages/geographic.py — Geographic Analysis."""
import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from dash_iconify import DashIconify
from services.data_service import (
    get_country_stats, get_city_stats, get_filter_options,
)
from utils.chart_themes import themed_layout, PRIMARY_COLORS
from utils.chart_config import GRAPH_CONFIG

dash.register_page(__name__, path="/geographic", name="Geographic Analysis",
                   title="Tourism Analytics | Geographic Analysis", order=3)

_opts = get_filter_options()
YEAR_OPTS   = [{"label": str(y), "value": y} for y in _opts["years"]]
SEASON_OPTS = [{"label": s, "value": s} for s in _opts["seasons"]]
TYPE_OPTS   = [{"label": t, "value": t} for t in _opts["tourist_types"]]


layout = html.Div(className="page-enter", children=[
    html.Div(className="page-header", children=[
        html.Div(className="page-header-top", children=[
            html.Div([
                html.H1("Geographic Analysis", className="page-title"),
                html.P("Destination performance by country and city", className="page-subtitle"),
            ]),
        ]),
    ]),

    # Filters
    html.Div(className="filter-panel", children=[
        html.Div(className="filter-row", children=[
            html.Div(className="filter-group", children=[
                html.Label("Year", className="filter-label"),
                dcc.Dropdown(id="geo-year-filter", options=YEAR_OPTS, multi=True, placeholder="All Years", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Season", className="filter-label"),
                dcc.Dropdown(id="geo-season-filter", options=SEASON_OPTS, multi=True, placeholder="All Seasons", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Tourist Type", className="filter-label"),
                dcc.Dropdown(id="geo-type-filter", options=TYPE_OPTS, multi=True, placeholder="All Types", className="filter-dropdown"),
            ]),
        ]),
    ]),

    # KPI Row
    html.Div(className="kpi-grid", style={"gridTemplateColumns":"repeat(4,1fr)"}, children=[
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Top Country (Visitors)", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:globe-2", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="geo-kpi-top-country"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Top City (Revenue)", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:building-2", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="geo-kpi-top-city"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Destinations", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:map-pin", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="geo-kpi-countries"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Avg Visitors per Country", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:users", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="geo-kpi-avg-visitors"),
        ]),
    ]),

    # Full width bar
    html.Div(className="chart-card", children=[
        html.Div(className="chart-card-header", children=[html.Span("Top 15 Countries by Visitors & Revenue", className="chart-card-title")]),
        dcc.Graph(id="geo-country-bar", config=GRAPH_CONFIG, style={"height": "400px"}),
    ]),

    # Treemap + City Bar
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1.5"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Country Visitor Distribution (Size=Visitors, Color=Revenue)", className="chart-card-title")]),
            dcc.Graph(id="geo-treemap", config=GRAPH_CONFIG, style={"height": "400px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Top 10 Cities", className="chart-card-title")]),
            dcc.Graph(id="geo-city-bar", config=GRAPH_CONFIG, style={"height": "400px"}),
        ]),
    ]),

    # Scatter + Sunburst
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Country Performance (Stay vs Rating)", className="chart-card-title")]),
            dcc.Graph(id="geo-bubble", config=GRAPH_CONFIG, style={"height": "400px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Revenue Concentration", className="chart-card-title")]),
            dcc.Graph(id="geo-sunburst", config=GRAPH_CONFIG, style={"height": "400px"}),
        ]),
    ]),

    # Rankings Table
    html.Div(className="chart-card", children=[
        html.Div(className="chart-card-header", children=[html.Span("Top 25 Country Rankings", className="chart-card-title")]),
        html.Div(className="table-container", id="geo-rankings-table")
    ]),

    # Insights
    html.Div(className="chart-card", id="geo-insights"),
])


@dash.callback(
    [Output("geo-kpi-top-country", "children"),
     Output("geo-kpi-top-city", "children"),
     Output("geo-kpi-countries", "children"),
     Output("geo-kpi-avg-visitors", "children"),
     Output("geo-country-bar", "figure"),
     Output("geo-treemap", "figure"),
     Output("geo-city-bar", "figure"),
     Output("geo-bubble", "figure"),
     Output("geo-sunburst", "figure"),
     Output("geo-rankings-table", "children"),
     Output("geo-insights", "children")],
    [Input("geo-year-filter", "value"),
     Input("geo-season-filter", "value"),
     Input("geo-type-filter", "value")],
    prevent_initial_call=False,
)
def update_geo(years, seasons, types):
    f = {}
    if years:   f["years"] = years
    if seasons: f["seasons"] = seasons
    if types:   f["tourist_types"] = types
    filters = f or None

    country_df = get_country_stats(filters)
    city_df    = get_city_stats(filters)

    # KPIs
    top_country = country_df.iloc[0]["Country"] if not country_df.empty else "N/A"
    top_city    = city_df.sort_values("Revenue", ascending=False).iloc[0]["City"] if not city_df.empty else "N/A"
    num_countries = len(country_df)
    avg_vis_per_c = int(country_df["Visitors"].mean()) if not country_df.empty else 0

    # ── Country Bar (Top 15) ─────────────────────────────────────────────
    fig_bar = go.Figure()
    top15_c = country_df.head(15).sort_values("Visitors", ascending=True)
    if not top15_c.empty:
        fig_bar.add_trace(go.Bar(
            y=top15_c["Country"], x=top15_c["Visitors"], orientation="h",
            marker=dict(color=top15_c["Revenue"], colorscale="Viridis", showscale=True, colorbar=dict(title="Revenue ($)")),
            text=[f"{v/1e3:.0f}K" for v in top15_c["Visitors"]], textposition="outside"
        ))
    fig_bar.update_layout(**themed_layout(True), xaxis_title="Visitors", yaxis_title="")

    # ── Treemap ──────────────────────────────────────────────────────────
    fig_tree = go.Figure()
    if not country_df.empty:
        fig_tree = px.treemap(country_df, path=[px.Constant("World"), "Country"],
                              values="Visitors", color="Revenue", color_continuous_scale="RdYlBu_r")
        fig_tree.update_traces(root_color="rgba(0,0,0,0)")
        fig_tree.update_layout(**themed_layout(True), margin=dict(t=10, l=10, r=10, b=10))

    # ── City Bar ─────────────────────────────────────────────────────────
    fig_city = go.Figure()
    top10_city = city_df.head(10).sort_values("Visitors", ascending=True)
    if not top10_city.empty:
        fig_city.add_trace(go.Bar(
            y=top10_city["City"], x=top10_city["Visitors"], orientation="h",
            marker_color="#F59E0B",
            text=[f"{v/1e3:.0f}K" for v in top10_city["Visitors"]], textposition="outside"
        ))
    fig_city.update_layout(**themed_layout(True), xaxis_title="Visitors", yaxis_title="")

    # ── Bubble Scatter ───────────────────────────────────────────────────
    fig_bubble = go.Figure()
    if not country_df.empty:
        fig_bubble = px.scatter(
            country_df, x="AvgStay", y="AvgRating", size="Visitors", color="Country",
            hover_name="Country", size_max=40, color_discrete_sequence=PRIMARY_COLORS
        )
        fig_bubble.update_layout(**themed_layout(True), xaxis_title="Average Stay (Days)", yaxis_title="Average Rating")

    # ── Sunburst (Country > City) ────────────────────────────────────────
    fig_sunburst = go.Figure()
    if not city_df.empty:
        # Get top 5 countries, then cities within them for cleaner sunburst
        top5 = country_df.head(5)["Country"].tolist()
        city_sub = city_df[city_df["Country"].isin(top5)]
        fig_sunburst = px.sunburst(city_sub, path=["Country", "City"], values="Revenue",
                                   color="Visitors", color_continuous_scale="Blues")
        fig_sunburst.update_layout(**themed_layout(True), margin=dict(t=10, l=10, r=10, b=10))

    # ── Rankings Table ───────────────────────────────────────────────────
    if not country_df.empty:
        rows = []
        for i, row in country_df.head(25).iterrows():
            rows.append(html.Tr([
                html.Td(f"#{i+1}"),
                html.Td(row["Country"], style={"fontWeight":"bold"}),
                html.Td(f"{row['Visitors']:,.0f}"),
                html.Td(f"${row['Revenue']:,.0f}"),
                html.Td(f"{row['AvgStay']:.1f}"),
                html.Td(f"{row['AvgRating']:.2f}")
            ]))
        table = html.Table(className="data-table", children=[
            html.Thead(html.Tr([html.Th("Rank"), html.Th("Country"), html.Th("Visitors"), html.Th("Revenue"), html.Th("Avg Stay"), html.Th("Avg Rating")])),
            html.Tbody(rows)
        ])
    else:
        table = html.Div("No data available.")

    # ── Insights ─────────────────────────────────────────────────────────
    insights = html.Div([
        html.Div(className="chart-card-header", children=[html.Span("💡 Geographic Insights", className="chart-card-title")]),
        html.Div(style={"display":"flex","flexWrap":"wrap","gap":"12px","padding":"16px"}, children=[
            html.Div(className="insight-item", children=[html.Span("🏆", className="insight-icon"), html.Span(f"Top Country: {top_country}.", className="insight-text")]),
            html.Div(className="insight-item", children=[html.Span("🏙️", className="insight-icon"), html.Span(f"Top Revenue City: {top_city}.", className="insight-text")]),
        ]),
    ])

    return (
        top_country, top_city, f"{num_countries:,}", f"{avg_vis_per_c:,.0f}",
        fig_bar, fig_tree, fig_city, fig_bubble, fig_sunburst, table, insights
    )
