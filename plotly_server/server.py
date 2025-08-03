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
    ci_history: list[float] = []
    ofi_history: list[float] = []
    app.layout = html.Div([
        dcc.Graph(id="depth-graph"),
        dcc.Graph(id="ci-graph"),
        dcc.Graph(id="ofi-graph"),
        dcc.Interval(id="interval", interval=1000, n_intervals=0),
    ])

    @app.callback(
        [
            dash.dependencies.Output("depth-graph", "figure"),
            dash.dependencies.Output("ci-graph", "figure"),
            dash.dependencies.Output("ofi-graph", "figure"),
        ],
        dash.dependencies.Input("interval", "n_intervals"),
    )
    def update_graph(n):  # pragma: no cover - UI callback
        df = metric_engine.buffer.depth_frame().to_pandas()
        metrics = metric_engine.compute()
        if df.empty:
            depth_fig = px.scatter()
        else:
            depth_fig = px.line(df, x=df.index, y=["data"])

        ci = metrics.get("CI")
        if ci is not None:
            ci_history.append(ci)
        ci_fig = (
            px.line(x=list(range(len(ci_history))), y=ci_history, labels={"x": "t", "y": "CI"})
            if ci_history
            else px.scatter()
        )

        ofi = metrics.get("OFI")
        if ofi is not None:
            ofi_history.append(ofi)
        ofi_fig = (
            px.line(x=list(range(len(ofi_history))), y=ofi_history, labels={"x": "t", "y": "OFI"})
            if ofi_history
            else px.scatter()
        )

        return depth_fig, ci_fig, ofi_fig

    return app


if __name__ == "__main__":  # pragma: no cover - manual run
    from data_buffer.buffer import DataBuffer
    from metric_engine.engine import MetricEngine

    buffer = DataBuffer()
    engine = MetricEngine(buffer)
    app = create_app(engine)
    app.run_server(debug=True)
