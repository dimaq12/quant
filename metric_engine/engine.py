"""Real‑time computation of market microstructure metrics."""
#@module:
#@  layer: domain
#@  depends: [typing, numpy, pandas, polars, settings.config, util.logger]
#@  exposes: [MetricEngine]
#@  restrictions: [ui.*, telegram_notifier.*]
#@end

from __future__ import annotations
from typing import Dict, Any
import numpy as np
import polars as pl
from util.logger import get_logger

_log = get_logger(__name__)

# Constants for sliding window calculations
DT = 0.1  # assumed seconds between depth samples
WINDOW_SHORT = 60  # trades
WINDOW_LONG = 300  # trades
ALPHA = 0.1  # smoothing for EMA
EPS = 1e-12

class MetricEngine:
    """Computes D, OFI, S, T_L, CI, φ, μ̇, κ in real‑time."""

    def __init__(self, buffer: "data_buffer.buffer.DataBuffer") -> None:
        self.buffer = buffer
        self.metrics: Dict[str, Any] = {}
        self._rate_ema: float = 0.0

    def _entropy(self, depth_df: pl.DataFrame) -> float:
        depth = depth_df.select(pl.all().exclude('type'))
        p = depth.sum(axis=0)
        p = p / p.sum()
        return float(-(p * np.log(p + 1e-12)).sum())

    def compute(self) -> Dict[str, Any]:
        """Compute microstructure metrics using buffered depth and trade data.

        Metrics are added to ``self.metrics`` as they become available.  If
        insufficient data exists for a metric it is left unchanged.
        """

        depth_df = self.buffer.depth_frame()
        if depth_df.height == 0:
            return self.metrics

        self.metrics['D'] = float(depth_df.select(pl.sum('data')).to_series()[0])
        S = self._entropy(depth_df)
        self.metrics['S'] = S
        S_norm = S / np.log(depth_df.height + EPS)
        self.metrics['CI'] = 1 - S_norm

        # ---- Depth based metrics -------------------------------------------------
        if depth_df.height >= 2:
            delta = (
                depth_df.select(pl.col('data').diff()).to_series().fill_null(0)
            )
            ofi = float(delta.sum())
            self.metrics['OFI'] = ofi
            scale = float(delta.abs().median()) or 1.0
            self.metrics['phi'] = float(np.tanh(ofi / (scale + EPS)))

            update_rate = depth_df.height
            self._rate_ema = ALPHA * update_rate + (1 - ALPHA) * self._rate_ema
            self.metrics['T_L'] = self._rate_ema / (self.metrics['D'] + EPS)
        else:
            _log.debug('insufficient depth data for OFI/T_L/phi')

        # ---- Trade based metrics -------------------------------------------------
        trade_df = self.buffer.trade_frame()
        if trade_df.height >= 2:
            price_series = trade_df.select(
                pl.col('data').struct.field('p').cast(float)
            ).to_series()
            prices = price_series.to_numpy()

            if prices.size > WINDOW_SHORT:
                mu = (prices[-1] - prices[-WINDOW_SHORT]) / (WINDOW_SHORT * DT)
            else:
                mu = (prices[-1] - prices[0]) / (max(prices.size - 1, 1) * DT)
            self.metrics['mu_dot'] = float(mu)

            log_returns = np.diff(np.log(prices))
            if log_returns.size > 0:
                window = log_returns[-WINDOW_LONG:]
                sigma = float(window.std())
            else:
                sigma = 0.0
            self.metrics['sigma'] = sigma

            tl = self.metrics.get('T_L', 0.0)
            self.metrics['kappa'] = sigma / (tl + EPS)
        else:
            _log.debug('insufficient trade data for mu_dot/kappa')

        return self.metrics
