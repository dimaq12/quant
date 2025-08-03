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
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stop_event = asyncio.Event()

    def every(self, seconds: int, coro: Callable[[], Awaitable[None]]) -> None:
        self._sched.add_job(coro, "interval", seconds=seconds)

    def start(self) -> asyncio.Task:
        _log.info("Scheduler starting")
        self._sched.start()
        self._stop_event.clear()
        self._loop = asyncio.get_event_loop()
        return self._loop.create_task(self._stop_event.wait())

    def stop(self) -> None:
        _log.info("Scheduler stopping")
        self._sched.shutdown(wait=False)
        self._stop_event.set()
        if self._loop and self._loop.is_running():
            self._loop.stop()
