"""Classifies market regime based on computed metrics."""
#@module:
#@  layer: domain
#@  depends: [typing, settings.config, util.logger]
#@  exposes: [StateEngine]
#@  restrictions: []
#@end

from typing import Dict, Any
from settings.config import settings
from util.logger import get_logger

_log = get_logger(__name__)

class StateEngine:
    """Determines regime: FLAT, TREND, TURBULENCE."""

    def __init__(self) -> None:
        self.regime: str | None = None

    def classify(self, metrics: Dict[str, Any]) -> str:
        CI = metrics.get('CI', 0)
        mu = abs(metrics.get('mu_dot', 0))
        sigma = metrics.get('sigma', 0)
        kappa = metrics.get('kappa', 0)
        k_c = settings.KAPPA_CRIT

        if CI > 0.6 and mu < settings.MU_EPS and sigma < settings.SIGMA_LOW:
            regime = "FLAT"
        elif mu >= settings.MU_EPS and sigma < settings.SIGMA_MED:
            regime = "TREND"
        elif sigma >= settings.SIGMA_HIGH or kappa > k_c:
            regime = "TURBULENCE"
        else:
            regime = self.regime or "FLAT"

        if regime != self.regime:
            _log.info("Regime transition %s → %s", self.regime, regime)
            self.regime = regime
        return regime
