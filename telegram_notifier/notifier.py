"""Telegram bot notifier."""
#@module:
#@  layer: ui
#@  depends: [typing, telegram, settings.config, util.logger]
#@  exposes: [TelegramNotifier]
#@  restrictions: []
#@end

from typing import Dict, Any
import asyncio
import telegram
from settings.config import settings
from util.logger import get_logger

_log = get_logger(__name__)

class TelegramNotifier:
    """Sends Telegram alerts on regime changes."""

    def __init__(self):
        self._bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)

    async def send_alert(self, regime: str, metrics: Dict[str, Any]) -> None:
        """Send an alert message to Telegram.

        Tries to send the message twice before giving up and logging the
        failure. Errors from the Telegram API are caught and logged.
        """
        text = f"Regime changed to {regime}\nMetrics: {metrics}"
        for attempt in range(2):
            try:
                await self._bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=text)
                break
            except telegram.error.TelegramError as exc:  # pragma: no cover - depends on external service
                _log.error("Failed to send Telegram message: %s", exc)
                if attempt == 0:
                    await asyncio.sleep(1)
