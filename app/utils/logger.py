"""
Custom thread-safe logger with optional UI listener callback.
"""
import logging
import sys
from typing import Callable, List

# Ensure Windows stdout supports UTF-8 characters without CharMapEncodeError
if sys.platform.startswith("win") and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

_UI_LISTENERS: List[Callable[[str], None]] = []


class UIStreamHandler(logging.Handler):
    """Logging handler that dispatches log lines to registered UI listeners."""
    def emit(self, record):
        try:
            msg = self.format(record)
            for listener in _UI_LISTENERS:
                try:
                    listener(msg)
                except Exception:
                    pass
        except Exception:
            self.handleError(record)


def register_ui_log_listener(callback: Callable[[str], None]):
    """Registers a callback to receive live log updates in the UI."""
    if callback not in _UI_LISTENERS:
        _UI_LISTENERS.append(callback)


def setup_logger(name: str = "social_scheduler") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", datefmt="%H:%M:%S")

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # UI handler
        uh = UIStreamHandler()
        uh.setFormatter(formatter)
        logger.addHandler(uh)

    return logger


logger = setup_logger()
