"""Logging setup for the BookGen command-line tools.

Loads a ``dictConfig`` from ``config/logging_config.json`` when present
(guideline 7.3), falling back to a basic stderr configuration. The ``level``
argument always takes precedence so callers can override verbosity.
"""

from __future__ import annotations

import json
import logging
import logging.config
import sys
from pathlib import Path

DEFAULT_LOGGING_CONFIG = Path("config/logging_config.json")


def configure_logging(
    level: int = logging.INFO,
    config_path: Path | str = DEFAULT_LOGGING_CONFIG,
) -> logging.Logger:
    """Configure logging from JSON (if present) and return the project logger."""
    path = Path(config_path)
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            logging.config.dictConfig(json.load(handle))
    else:
        logging.basicConfig(
            level=level, format="%(levelname)s: %(message)s", stream=sys.stderr, force=True
        )

    logging.getLogger().setLevel(level)
    logger = logging.getLogger("bookgen")
    logger.setLevel(level)
    return logger
