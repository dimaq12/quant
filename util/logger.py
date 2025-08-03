"""Centralized logging configuration."""
import logging
from typing import Optional

_FORMAT = "%(asctime)s %(levelname)s %(name)s ‑ %(message)s"
_handler: Optional[logging.Handler] = None

def get_logger(name: str) -> logging.Logger:
    global _handler
    if _handler is None:
        _handler = logging.StreamHandler()
        _handler.setFormatter(logging.Formatter(_FORMAT))
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.addHandler(_handler)
    return logging.getLogger(name)
