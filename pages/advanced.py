"""pages/advanced.py — Advanced Analytics."""
import dash
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from dash_iconify import DashIconify
from services.data_service import (
    get_correlation_matrix, get_numeric_data, get_outlier_data,
    get_statistical_summary, get_clustering_data, get_filter_options
)
from utils.chart_themes import themed_layout, PRIMARY_COLORS
from utils.chart_config import GRAPH_CONFIG

dash.register_page(__name__, path="/advanced", name="Advanced Analytics",
                   title="Tourism Analytics | Advanced Analytics", order=7)

_opts = get_filter_options()
YEAR_OPTS    = [{"label": str(y), "value": y} for y in _opts["years"]]
COUNTRY_OPTS = [{"label": c, "value": c} for c in _opts["countries"]]

layout = html.Div(className="page-enter", children=[
    html.Div(className="page-header", children=[
        html.Div(className="page-header-top", children=[
            html.Div([
                html.H1("Advanced Analytics", className="page-title"),
                html.P("Correlation, outliers, and clustering analysis", className="page-subtitle"),
            ]),
        ]),
    ]),

    # Filters
    html.Div(className="filter-panel", children=[
        html.Div(className="filter-row", children=[
            html.Div(className="filter-group", children=[
                html.Label("Year", className="filter-label"),
                dcc.Dropdown(id="adv-year-filter", options=YEAR_OPTS, multi=True, placeholder="All Years", className="filter-dropdown"),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Country", className="filter-label"),
                dcc.Dropdown(id="adv-country-filter", options=COUNTRY_OPTS, multi=True, placeholder="All Countries", className="filter-dropdown"),
            ]),
        ]),
    ]),

    # KPI Row
    html.Div(className="kpi-grid", style={"gridTemplateColumns":"repeat(4,1fr)"}, children=[
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Top Correlation", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:git-commit", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="adv-kpi-corr-pair"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Revenue Driver", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:dollar-sign", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="adv-kpi-top-corr"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Outliers Detected", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:alert-circle", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="adv-kpi-outliers"),
        ]),
        html.Div(className="kpi-card", children=[
            html.Div(className="kpi-card-header", children=[html.Span("K-Means Clusters", className="kpi-card-label"), html.Div(DashIconify(icon="lucide:network", width=20), className="kpi-card-icon-wrap")]),
            html.Div("—", className="kpi-card-value", id="adv-kpi-clusters"),
        ]),
    ]),

    # Heatmap + Stats
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Correlation Matrix", className="chart-card-title")]),
            dcc.Graph(id="adv-corr-heatmap", config=GRAPH_CONFIG, style={"height": "400px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Statistical Summary", className="chart-card-title")]),
            html.Div(className="table-container", id="adv-stats-div")
        ]),
    ]),

    # Outliers
    html.Div(className="chart-card", children=[
        html.Div(className="chart-card-header", children=[html.Span("Outlier Detection (Visitors vs Revenue)", className="chart-card-title")]),
        dcc.Graph(id="adv-outlier-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
    ]),

    # Clustering + Box plots
    html.Div(className="chart-grid", children=[
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Country Clustering (K-Means)", className="chart-card-title")]),
            dcc.Graph(id="adv-cluster-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
        ]),
        html.Div(className="chart-card", style={"flex": "1"}, children=[
            html.Div(className="chart-card-header", children=[html.Span("Metric Distributions", className="chart-card-title")]),
            dcc.Graph(id="adv-box-chart", config=GRAPH_CONFIG, style={"height": "400px"}),
        ]),
    ]),

    # Distribution
    html.Div(className="chart-card", children=[
        html.Div(className="chart-card-header", children=[html.Span("Visitor Volume Distribution", className="chart-card-title")]),
        dcc.Graph(id="adv-hist-chart", config=GRAPH_CONFIG, style={"height": "350px"}),
    ]),

    # Insights
    html.Div(className="chart-card", id="adv-insights"),
])


@dash.callback(
    [Output("adv-kpi-corr-pair", "children"),
     Output("adv-kpi-top-corr", "children"),
     Output("adv-kpi-outliers", "children"),
     Output("adv-kpi-clusters", "children"),
     Output("adv-corr-heatmap", "figure"),
     Output("adv-stats-div", "children"),
     Output("adv-outlier-chart", "figure"),
     Output("adv-cluster-chart", "figure"),
     Output("adv-box-chart", "figure"),
     Output("adv-hist-chart", "figure"),
     Output("adv-insights", "children")],
    [Input("adv-year-filter", "value"),
     Input("adv-country-filter", "value")],
    prevent_initial_call=False,
)
def update_adv(years, countries):
    f = {}
    if years: f["years"] = years
    if countries: f["countries"] = countries
    filters = f or None

    corr_df = get_correlation_matrix(filters)
    num_df  = get_numeric_data(filters)
    out_df  = get_outlier_data(filters)
    stat_df = get_statistical_summary(filters)
    clus_df = get_clustering_data(4, filters)

    # 1. KPIs
    top_pair = "N/A"
    top_rev  = "N/A"
    out_count = out_df["Visitors_outlier"].sum() + out_df["Revenue_USD_outlier"].sum() if not out_df.empty else 0
    num_clus = clus_df["Cluster"].nunique() if not clus_df.empty else 0

    if not corr_df.empty:
        c = corr_df.unstack()
        c = c[c < 1.0].sort_values(ascending=False)
        if not c.empty:
            p1, p2 = c.index[0]
            top_pair = f"{p1} & {p2} ({c.iloc[0]:.2f})"
        
        rev_corr = corr_df["Revenue_USD"].drop("Revenue_USD").sort_values(ascending=False)
        if not rev_corr.empty:
            top_rev = f"{rev_corr.index[0]} ({rev_corr.iloc[0]:.2f})"

    # 2. Heatmap
    fig_corr = go.Figure()
    if not corr_df.empty:
        fig_corr.add_trace(go.Heatmap(
            z=corr_df.values, x=corr_df.columns, y=corr_df.index,
            colorscale="RdBu", zmin=-1, zmax=1,
            text=corr_df.round(2).values, texttemplate="%{text}"
        ))
    fig_corr.update_layout(**themed_layout(True), margin=dict(l=120, b=100))

    # 3. Stats Table
    table = html.Div("No data")
    if not stat_df.empty:
        cols = stat_df.columns
        rows = [html.Tr([html.Td(row[c]) for c in cols]) for _, row in stat_df.iterrows()]
        table = html.Table(className="data-table", children=[
            html.Thead(html.Tr([html.Th(c) for c in cols])),
            html.Tbody(rows)
        ])

    # 4. Outliers Scatter
    fig_out = go.Figure()
    if not out_df.empty:
        out_df["IsOutlier"] = out_df["Visitors_outlier"] | out_df["Revenue_USD_outlier"]
        colors = ["#EF4444" if o else "#3B82F6" for o in out_df["IsOutlier"]]
        fig_out.add_trace(go.Scatter(
            x=out_df["Visitors"], y=out_df["Revenue_USD"], mode="markers",
            marker=dict(color=colors, size=6, opacity=0.6),
            text=["Outlier" if o else "Normal" for o in out_df["IsOutlier"]], hoverinfo="x+y+text"
        ))
    fig_out.update_layout(**themed_layout(True), xaxis_title="Visitors", yaxis_title="Revenue ($)")

    # 5. Clusters
    fig_clus = go.Figure()
    if not clus_df.empty:
        fig_clus = px.scatter(
            clus_df, x="AvgStay", y="AvgRating", color="Cluster", size="Visitors",
            hover_name="Country", color_discrete_sequence=PRIMARY_COLORS
        )
        fig_clus.update_layout(**themed_layout(True), xaxis_title="Average Stay", yaxis_title="Average Rating")
    else:
        fig_clus.update_layout(**themed_layout(True)).add_annotation(
            text="Sklearn not available or insufficient data for clustering.",
            showarrow=False, font=dict(size=14)
        )

    # 6. Box plots
    fig_box = go.Figure()
    if not num_df.empty:
        for c, color in zip(["Average_Stay_Days", "Customer_Rating", "Hotel_Occupancy"], PRIMARY_COLORS):
            fig_box.add_trace(go.Box(y=num_df[c], name=c, marker_color=color))
    fig_box.update_layout(**themed_layout(True))

    # 7. Histogram
    fig_hist = go.Figure()
    if not num_df.empty:
        fig_hist.add_trace(go.Histogram(x=num_df["Visitors"], nbinsx=50, marker_color="#8B5CF6"))
    fig_hist.update_layout(**themed_layout(True), xaxis_title="Visitors", yaxis_title="Frequency")

    insights = html.Div([
        html.Div(className="chart-card-header", children=[html.Span("💡 Advanced Insights", className="chart-card-title")]),
        html.Div(style={"display":"flex","flexWrap":"wrap","gap":"12px","padding":"16px"}, children=[
            html.Div(className="insight-item", children=[html.Span("🔗", className="insight-icon"), html.Span(f"Strongest correlation: {top_pair}.", className="insight-text")]),
            html.Div(className="insight-item", children=[html.Span("⚠️", className="insight-icon"), html.Span(f"Outliers detected: {out_count}.", className="insight-text")]),
        ]),
    ])

    return (
        top_pair, top_rev, f"{out_count:,}", f"{num_clus}",
        fig_corr, table, fig_out, fig_clus, fig_box, fig_hist, insights
    )
