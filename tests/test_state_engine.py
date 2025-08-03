from state_engine.state import StateEngine


def test_classify_flat():
    engine = StateEngine()
    metrics = {"CI": 0.7, "mu_dot": 0.0, "sigma": 0.0005}
    assert engine.classify(metrics) == "FLAT"


def test_classify_trend():
    engine = StateEngine()
    metrics = {"mu_dot": 0.1, "sigma": 0.005}
    assert engine.classify(metrics) == "TREND"


def test_classify_turbulence():
    engine = StateEngine()
    metrics = {"sigma": 0.06}
    assert engine.classify(metrics) == "TURBULENCE"


def test_regime_persistence():
    engine = StateEngine()
    engine.classify({"mu_dot": 0.1, "sigma": 0.005})
    assert engine.classify({"sigma": 0.02}) == "TREND"
