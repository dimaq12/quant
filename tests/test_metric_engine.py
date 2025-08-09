import pytest

from data_buffer.buffer import DataBuffer
from metric_engine.engine import MetricEngine


def test_compute_basic_metrics():
    buf = DataBuffer()
    buf.append({'type': 'depth', 'data': 2})
    engine = MetricEngine(buf)
    engine._entropy = lambda df: 0.0
    metrics = engine.compute()

    assert metrics.D == 2
    assert metrics.CI == 1.0
    assert metrics.OFI == 0.0


def test_compute_full_metrics():
    buf = DataBuffer()
    buf.append({'type': 'depth', 'data': 1})
    buf.append({'type': 'depth', 'data': 2})
    buf.append({'type': 'trade', 'data': {'p': 100}})
    buf.append({'type': 'trade', 'data': {'p': 101}})
    engine = MetricEngine(buf)
    engine._entropy = lambda df: 0.0
    metrics = engine.compute()

    assert metrics.OFI == 1.0
    assert metrics.mu_dot == pytest.approx(10.0)
    assert metrics.phi > 0.0
    assert metrics.T_L > 0.0
    assert metrics.sigma >= 0.0
    assert metrics.kappa >= 0.0
