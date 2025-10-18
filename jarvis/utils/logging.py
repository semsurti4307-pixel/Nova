import logging
import sys
from typing import Optional


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logger with a sensible default format.

    The function is idempotent; calling it multiple times will not duplicate handlers.
    """
    root_logger = logging.getLogger()
    if any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.setLevel(level)
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name if name else __name__)
