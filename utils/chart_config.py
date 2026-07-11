"""
utils/chart_config.py — Shared Plotly / dcc.Graph configuration.

Import GRAPH_CONFIG into every dcc.Graph component to ensure:
  • No "Deploy" (sendDataToCloud) button
  • No Plotly logo
  • Consistent modebar with only useful tools
  • High-res PNG export on download
"""

# Standard config applied to every dcc.Graph in the app
GRAPH_CONFIG: dict = {
    # Show the modebar only on hover (cleaner look)
    "displayModeBar": "hover",

    # Remove unwanted buttons:
    #   sendDataToCloud  → the "Deploy" button
    #   lasso2d / select2d → box/lasso selection (not needed for BI)
    "modeBarButtonsToRemove": [
        "sendDataToCloud",
        "lasso2d",
        "select2d",
        "autoScale2d",
    ],

    # Remove Plotly logo from modebar
    "displaylogo": False,

    # High-quality PNG export when user clicks download
    "toImageButtonOptions": {
        "format": "png",
        "filename": "tourism_analytics",
        "height": 600,
        "width": 1200,
        "scale": 2,          # Retina quality
    },

    # Disable the "Edit in Chart Studio" link on hover
    "showEditInChartStudio": False,
    "showLink": False,
}
