"""pages/explorer.py — Data Explorer."""
import dash
from dash import html, dcc, Input, Output, State, dash_table
import plotly.graph_objects as go
from dash_iconify import DashIconify
from services.data_service import get_df, get_data_quality_stats, get_filter_options
from utils.chart_themes import themed_layout
from utils.chart_config import GRAPH_CONFIG
import pandas as pd

dash.register_page(__name__, path="/explorer", name="Data Explorer",
                   title="Tourism Analytics | Data Explorer", order=9)

_opts = get_filter_options()
YEAR_OPTS    = [{"label": str(y), "value": y} for y in _opts["years"]]
COUNTRY_OPTS = [{"label": c, "value": c} for c in _opts["countries"]]
TYPE_OPTS    = [{"label": t, "value": t} for t in _opts["tourist_types"]]

# Compute static quality cards & distributions once at module load
qual = get_data_quality_stats()
df = get_df()

fig_vh = go.Figure(go.Histogram(x=df["Visitors"], nbinsx=30, marker_color="#6366F1")).update_layout(**themed_layout(True)).update_layout(margin=dict(t=20, b=20), height=250)
fig_rh = go.Figure(go.Histogram(x=df["Revenue_USD"], nbinsx=30, marker_color="#10B981")).update_layout(**themed_layout(True)).update_layout(margin=dict(t=20, b=20), height=250)

top_c = df.groupby("Country")["Visitors"].sum().nlargest(10).reset_index()
fig_cb = go.Figure(go.Bar(x=top_c["Country"], y=top_c["Visitors"], marker_color="#F59E0B")).update_layout(**themed_layout(True)).update_layout(margin=dict(t=20, b=20), height=250)

top_t = df.groupby("Tourist_Type")["Visitors"].sum().reset_index()
fig_tp = go.Figure(go.Pie(labels=top_t["Tourist_Type"], values=top_t["Visitors"], hole=0.5)).update_layout(**themed_layout(True)).update_layout(margin=dict(t=20, b=20), height=250)

layout = html.Div(className="page-enter", children=[
    html.Div(className="page-header animate-on-scroll fade-up", children=[
        html.Div(className="page-header-top", children=[
            html.Div([
                html.H1("Data Explorer", className="page-title"),
                html.P("Raw data inspection, quality metrics, and CSV export", className="page-subtitle"),
            ]),
        ]),
    ]),

    # Filters & Search
    html.Div(className="filter-panel animate-on-scroll fade-up stagger-1", children=[
        html.Div(className="filter-row", children=[
            html.Div(className="filter-group", children=[
                html.Label("Search", className="filter-label"),
                dcc.Input(id="exp-search", type="text", placeholder="Search anything...", debounce=True, className="filter-dropdown", style={"padding":"8px", "width":"200px"}),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Year", className="filter-label"),
                dcc.Dropdown(id="exp-year-filter", options=YEAR_OPTS, multi=True, placeholder="All Years", className="filter-dropdown", style={"minWidth":"120px"}),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Country", className="filter-label"),
                dcc.Dropdown(id="exp-country-filter", options=COUNTRY_OPTS, multi=True, placeholder="All Countries", className="filter-dropdown", style={"minWidth":"200px"}),
            ]),
            html.Div(className="filter-group", children=[
                html.Label("Tourist Type", className="filter-label"),
                dcc.Dropdown(id="exp-type-filter", options=TYPE_OPTS, multi=True, placeholder="All Types", className="filter-dropdown", style={"minWidth":"150px"}),
            ]),
            html.Div(className="filter-group", style={"alignSelf":"flex-end", "marginLeft":"auto"}, children=[
                html.Button("Download CSV", id="exp-download-btn", className="btn btn-primary btn-sm"),
                dcc.Download(id="exp-download")
            ]),
        ]),
    ]),

    # Quality Cards (Static)
    html.Div(className="kpi-grid animate-on-scroll fade-up stagger-1", style={"gridTemplateColumns":"repeat(5,1fr)"}, children=[
        html.Div(className="kpi-card animate-on-scroll fade-up", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Total Rows", className="kpi-card-label")]),
            html.Div(f"{qual['total_rows']:,}", className="kpi-card-value"),
        ]),
        html.Div(className="kpi-card animate-on-scroll fade-up", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Columns", className="kpi-card-label")]),
            html.Div(f"{qual['total_cols']}", className="kpi-card-value"),
        ]),
        html.Div(className="kpi-card animate-on-scroll fade-up", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Missing Values", className="kpi-card-label")]),
            html.Div(f"{qual['missing']}", className="kpi-card-value"),
        ]),
        html.Div(className="kpi-card animate-on-scroll fade-up", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Duplicates", className="kpi-card-label")]),
            html.Div(f"{qual['duplicates']}", className="kpi-card-value"),
        ]),
        html.Div(className="kpi-card animate-on-scroll fade-up", children=[
            html.Div(className="kpi-card-header", children=[html.Span("Date Range", className="kpi-card-label")]),
            html.Div(qual['date_range'], className="kpi-card-value", style={"fontSize":"20px"}),
        ]),
    ]),

    # Dist charts
    html.Div(className="chart-grid animate-on-scroll fade-up stagger-2", style={"gridTemplateColumns":"repeat(4,1fr)"}, children=[
        html.Div(className="chart-card animate-on-scroll fade-up stagger-3", children=[
            html.Div(className="chart-card-header", children=[html.Span("Visitors Dist", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(figure=fig_vh, config=GRAPH_CONFIG),
                type="circle", color="#6366F1"
            ),
        ]),
        html.Div(className="chart-card animate-on-scroll fade-up stagger-3", children=[
            html.Div(className="chart-card-header", children=[html.Span("Revenue Dist", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(figure=fig_rh, config=GRAPH_CONFIG),
                type="circle", color="#6366F1"
            ),
        ]),
        html.Div(className="chart-card animate-on-scroll fade-up stagger-3", children=[
            html.Div(className="chart-card-header", children=[html.Span("Top Countries", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(figure=fig_cb, config=GRAPH_CONFIG),
                type="circle", color="#6366F1"
            ),
        ]),
        html.Div(className="chart-card animate-on-scroll fade-up stagger-3", children=[
            html.Div(className="chart-card-header", children=[html.Span("Tourist Types", className="chart-card-title")]),
            dcc.Loading(
                dcc.Graph(figure=fig_tp, config=GRAPH_CONFIG),
                type="circle", color="#6366F1"
            ),
        ]),
    ]),

    # Stats Table
    html.Div(className="chart-card animate-on-scroll fade-up stagger-3", children=[
        html.Div(className="chart-card-header", children=[html.Span("Statistical Summary (Filtered)", className="chart-card-title")]),
        dcc.Loading(
            html.Div(className="table-container", id="exp-stats-div"),
            type="circle", color="#6366F1"
        )
    ]),

    # Data Table
    html.Div(className="chart-card animate-on-scroll fade-up stagger-3", children=[
        html.Div(className="chart-card-header", children=[
            html.Span("Dataset Explorer", className="chart-card-title"),
            html.Span(" (showing up to 1000 rows for performance)", style={"color":"#94A3B8","fontSize":"12px"})
        ]),
        dcc.Loading(
            dash_table.DataTable(
                id="exp-data-table",
                page_size=15,
                sort_action="native",
                filter_action="native",
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": "#1A2540",
                    "color": "#F1F5F9",
                    "fontWeight": "600",
                    "border": "1px solid rgba(255,255,255,0.06)"
                },
                style_cell={
                    "backgroundColor": "#0F1729",
                    "color": "#94A3B8",
                    "border": "1px solid rgba(255,255,255,0.06)",
                    "padding": "10px 12px",
                    "fontSize": "12px",
                    "textAlign": "left"
                },
                style_data_conditional=[{
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#141E33"
                }],
            ),
            type="circle", color="#6366F1"
        )
    ]),
])

def _filter_df(years, countries, types, search):
    d = df.copy()
    if years: d = d[d["Year"].isin(years)]
    if countries: d = d[d["Country"].isin(countries)]
    if types: d = d[d["Tourist_Type"].isin(types)]
    if search:
        mask = d.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        d = d[mask]
    return d

@dash.callback(
    [Output("exp-data-table", "data"),
     Output("exp-data-table", "columns"),
     Output("exp-stats-div", "children")],
    [Input("exp-year-filter", "value"),
     Input("exp-country-filter", "value"),
     Input("exp-type-filter", "value"),
     Input("exp-search", "value")],
    prevent_initial_call=False,
)
def update_table(years, countries, types, search):
    filtered = _filter_df(years, countries, types, search)
    
    # Exclude ID
    display_df = filtered.drop(columns=["Tourist_ID"], errors="ignore")
    
    cols = [{"name": i, "id": i} for i in display_df.columns]
    data = display_df.head(1000).to_dict("records")
    
    # Stats table
    num_df = display_df.select_dtypes(include=["number"])
    if not num_df.empty:
        stat_df = num_df.describe().round(2).reset_index().rename(columns={"index": "Statistic"})
        scols = stat_df.columns
        srows = [html.Tr([html.Td(row[c]) for c in scols]) for _, row in stat_df.iterrows()]
        table = html.Table(className="data-table", children=[
            html.Thead(html.Tr([html.Th(c) for c in scols])),
            html.Tbody(srows)
        ])
    else:
        table = html.Div("No numeric data")
        
    return data, cols, table

@dash.callback(
    Output("exp-download", "data"),
    Input("exp-download-btn", "n_clicks"),
    [State("exp-year-filter", "value"),
     State("exp-country-filter", "value"),
     State("exp-type-filter", "value"),
     State("exp-search", "value")],
    prevent_initial_call=True,
)
def download_csv(n, years, countries, types, search):
    filtered = _filter_df(years, countries, types, search)
    return dcc.send_data_frame(filtered.to_csv, "tourism_data.csv", index=False)
