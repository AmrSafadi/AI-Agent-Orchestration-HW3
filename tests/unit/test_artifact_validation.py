"""Tests for canonical-artifact validation (write_valid_artifact)."""

from __future__ import annotations

from pathlib import Path

from bookgen.orchestration.artifact_validation import write_valid_artifact


def test_empty_manuscript_is_rejected(tmp_path: Path) -> None:
    assert (
        write_valid_artifact("manuscript", "   ", tmp_path / "m.md") == "manuscript output is empty"
    )


def test_unknown_artifact_name_is_rejected(tmp_path: Path) -> None:
    assert write_valid_artifact("mystery", "{}", tmp_path / "x.json") is not None


def test_invalid_json_is_rejected(tmp_path: Path) -> None:
    error = write_valid_artifact("book_plan", "not json at all", tmp_path / "bp.json")
    assert error is not None
    assert not (tmp_path / "bp.json").exists()  # nothing written on failure
