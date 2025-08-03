import pytest

from data_buffer.buffer import DataBuffer
from metric_engine.engine import MetricEngine


def test_compute_basic_metrics():
    buf = DataBuffer()
    buf.append({'type': 'depth', 'data': 2})
    engine = MetricEngine(buf)
    engine._entropy = lambda df: 0.0
    metrics = engine.compute()

    assert metrics['D'] == 2
    assert 'CI' in metrics
    assert 'OFI' not in metrics


def test_compute_full_metrics():
    buf = DataBuffer()
    buf.append({'type': 'depth', 'data': 1})
    buf.append({'type': 'depth', 'data': 2})
    buf.append({'type': 'trade', 'data': {'p': 100}})
    buf.append({'type': 'trade', 'data': {'p': 101}})
    engine = MetricEngine(buf)
    engine._entropy = lambda df: 0.0
    metrics = engine.compute()

    assert metrics['OFI'] == 1.0
    assert metrics['mu_dot'] == pytest.approx(10.0)
    for key in ['phi', 'T_L', 'sigma', 'kappa']:
        assert key in metrics
