import os
import sys
import types
from pathlib import Path

# Ensure required environment variables for settings are present
os.environ.setdefault("TELEGRAM_TOKEN", "dummy")
os.environ.setdefault("TELEGRAM_CHAT_ID", "dummy")

# Make project root importable
sys.path.append(str(Path(__file__).resolve().parents[1]))

# Provide lightweight settings module to avoid pydantic dependency
class _Settings:
    SYMBOL = "BTCUSDT"
    RAW_BUFFER_MINUTES = 5
    TRADES_PER_SEC = 50
    MU_EPS = 1e-5
    SIGMA_LOW = 0.001
    SIGMA_MED = 0.01
    SIGMA_HIGH = 0.05
    KAPPA_CRIT = 1.0

settings = _Settings()
module = types.SimpleNamespace(Settings=_Settings, settings=settings)
sys.modules.setdefault("settings.config", module)
