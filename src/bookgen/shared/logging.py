"""Logging setup for the BookGen command-line tools."""

from __future__ import annotations

import logging
import sys


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure console logging and return the project logger."""
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )
    return logging.getLogger("bookgen")
