"""Telegram bot notifier."""
#@module:
#@  layer: ui
#@  depends: [typing, telegram, settings.config, util.logger]
#@  exposes: [TelegramNotifier]
#@  restrictions: []
#@end

from typing import Dict, Any
import telegram
from settings.config import settings
from util.logger import get_logger

_log = get_logger(__name__)

class TelegramNotifier:
    """Sends Telegram alerts on regime changes."""

    def __init__(self):
        self._bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)

    def send_alert(self, regime: str, metrics: Dict[str, Any]) -> None:
        text = f"Regime changed to {regime}\nMetrics: {metrics}"
        self._bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=text)
