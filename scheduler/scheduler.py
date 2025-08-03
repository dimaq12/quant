"""Async orchestration and scheduling."""
#@module:
#@  layer: app
#@  depends: [typing, apscheduler.schedulers.asyncio, asyncio, util.logger]
#@  exposes: [Scheduler]
#@  restrictions: []
#@end

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Awaitable, Callable
from util.logger import get_logger

_log = get_logger(__name__)

class Scheduler:
    """High‑level scheduler registering periodic tasks."""

    def __init__(self):
        self._sched = AsyncIOScheduler()

    def every(self, seconds: int, coro: Callable[[], Awaitable[None]]) -> None:
        self._sched.add_job(coro, "interval", seconds=seconds)

    def start(self) -> None:
        _log.info("Scheduler starting")
        self._sched.start()
        asyncio.get_event_loop().run_forever()
