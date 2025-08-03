"""In‑memory circular buffer for tick data."""
#@module:
#@  layer: infra
#@  depends: [typing, collections, pandas, polars, settings.config, util.logger]
#@  exposes: [DataBuffer]
#@  restrictions: [domain.*]
#@end

import collections
from typing import Any, Deque

import polars as pl
from settings.config import settings
from util.logger import get_logger

_log = get_logger(__name__)

class DataBuffer:
    """Ring buffer storing last N minutes of depth & trades."""

    def __init__(self, minutes: int | None = None) -> None:
        self.minutes = minutes or settings.RAW_BUFFER_MINUTES
        self._depth: Deque[dict[str, Any]] = collections.deque(maxlen=self.minutes * 600)  # 100ms
        self._trades: Deque[dict[str, Any]] = collections.deque(maxlen=self.minutes * 60 * settings.TRADES_PER_SEC)

    def append(self, item: dict[str, Any]) -> None:
        if "type" not in item or "data" not in item:
            raise KeyError("item must contain 'type' and 'data'")

        if item["type"] == "depth":
            self._depth.append(item)
        elif item["type"] == "trade":
            self._trades.append(item)
        else:
            _log.error("unknown item type: %s", item["type"])
            raise ValueError(f"unknown item type: {item['type']}")

    def depth_frame(self) -> pl.DataFrame:
        return pl.DataFrame(self._depth)

    def trade_frame(self) -> pl.DataFrame:
        return pl.DataFrame(self._trades)
