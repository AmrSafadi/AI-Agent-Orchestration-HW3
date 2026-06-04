"""Tests for the logging configuration helper."""

from __future__ import annotations

import logging

from bookgen.shared.logging import configure_logging


def test_returns_named_bookgen_logger() -> None:
    logger = configure_logging()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "bookgen"


def test_sets_root_level() -> None:
    configure_logging(level=logging.DEBUG)
    assert logging.getLogger().level == logging.DEBUG
    configure_logging(level=logging.INFO)


def test_emits_formatted_record_to_stderr(capsys) -> None:
    logger = configure_logging()
    logger.warning("hello-test-record")
    captured = capsys.readouterr()
    assert "WARNING: hello-test-record" in captured.err
