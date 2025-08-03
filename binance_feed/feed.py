"""Real‑time Binance order book & trade feed."""
#@module:
#@  layer: infra
#@  depends: [typing, asyncio, aiohttp, websockets, settings.config, util.logger]
#@  exposes: [BinanceFeed]
#@  restrictions: [domain.*]
#@end

import asyncio, json, contextlib
import aiohttp
from typing import Any
from settings.config import settings
from util.logger import get_logger

_log = get_logger(__name__)

#@contract:
#@  pre: symbol.isupper() and len(symbol) >= 6
#@  post: result is None
#@  assigns: [self._queue]
#@end
class BinanceFeed:
    """Streams Binance depth & trade events into an asyncio.Queue."""

    def __init__(
        self,
        symbol: str,
        queue: "asyncio.Queue[dict[str, Any]]",
        max_retries: int | None = None,
        retry_delay: float | None = None,
    ) -> None:
        self.symbol = symbol.lower()
        self._queue = queue
        self._ws_url = f"wss://stream.binance.com:9443/stream?streams={self.symbol}@depth@100ms/{self.symbol}@trade"
        self._task: asyncio.Task | None = None
        self._max_retries = (
            max_retries if max_retries is not None else settings.WS_MAX_RETRIES
        )
        self._retry_delay = (
            retry_delay if retry_delay is not None else settings.WS_RETRY_DELAY
        )

    async def _listen(self) -> None:
        attempt = 0
        delay = self._retry_delay
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(self._ws_url) as ws:
                        _log.info(
                            "Binance WebSocket connected for %s", self.symbol.upper()
                        )
                        async for msg in ws:
                            if msg.type != aiohttp.WSMsgType.TEXT:
                                continue
                            data = json.loads(msg.data)
                            stream = data.get("stream", "")
                            payload = data.get("data", {})
                            if stream.endswith("@depth"):
                                await self._queue.put({"type": "depth", "data": payload})
                            elif stream.endswith("@trade"):
                                await self._queue.put({"type": "trade", "data": payload})
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                attempt += 1
                _log.warning(
                    "WebSocket error for %s: %s", self.symbol.upper(), exc
                )
                if attempt >= self._max_retries:
                    _log.error("Max retries exceeded for %s", self.symbol.upper())
                    break
                _log.info("Reconnecting in %.1f seconds", delay)
                await asyncio.sleep(delay)
                delay *= 2
            else:
                attempt = 0
                delay = self._retry_delay

    async def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._listen())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
