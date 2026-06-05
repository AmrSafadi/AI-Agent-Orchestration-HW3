"""Tests for the centralized version (guideline 8.1)."""

from __future__ import annotations

from bookgen.shared.version import __version__, get_version


def test_get_version_matches_dunder() -> None:
    assert get_version() == __version__


def test_version_is_semver_like() -> None:
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
