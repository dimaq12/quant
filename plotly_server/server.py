"""Dash‑based real‑time UI server."""
#@module:
#@  layer: ui
#@  depends: [dash, plotly.express, pandas, polars, settings.config, util.logger, domain.metric_engine]
#@  exposes: [create_app]
#@  restrictions: []
#@end

import dash
from dash import dcc, html
import plotly.express as px
from util.logger import get_logger

_log = get_logger(__name__)

def create_app(metric_engine: "metric_engine.engine.MetricEngine") -> dash.Dash:
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Graph(id="depth-graph"),
        dcc.Interval(id="interval", interval=1000, n_intervals=0),
    ])

    @app.callback(
        dash.dependencies.Output("depth-graph", "figure"),
        dash.dependencies.Input("interval", "n_intervals"),
    )
    def update_graph(n):
        df = metric_engine.buffer.depth_frame().to_pandas()
        if df.empty:
            return px.scatter()
        return px.line(df, x=df.index, y=["data"])

    return app
