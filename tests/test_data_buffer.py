import polars as pl
import pytest

from data_buffer.buffer import DataBuffer


def test_append_and_frames():
    buf = DataBuffer(minutes=1)
    buf.append({"type": "depth", "data": 1})
    buf.append({"type": "trade", "data": {"p": 10}})

    depth_df = buf.depth_frame()
    trade_df = buf.trade_frame()

    assert depth_df.height == 1
    assert depth_df["data"][0] == 1
    assert trade_df.height == 1
    assert trade_df["data"][0]["p"] == 10


def test_append_missing_fields_raises():
    buf = DataBuffer()
    with pytest.raises(KeyError):
        buf.append({"type": "depth"})
    with pytest.raises(KeyError):
        buf.append({"data": 1})


def test_append_unknown_type_raises():
    buf = DataBuffer()
    with pytest.raises(ValueError):
        buf.append({"type": "other", "data": 1})
