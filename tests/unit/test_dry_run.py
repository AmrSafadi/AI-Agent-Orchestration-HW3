"""Tests for dry-run artifact synthesis and its safe fallbacks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bookgen.orchestration import dry_run
from bookgen.orchestration.dry_run import (
    _create_dry_run_artifact,
    create_or_reuse_dry_run_artifacts,
)


def test_create_or_reuse_copies_all_samples(tmp_path: Path) -> None:
    artifacts = create_or_reuse_dry_run_artifacts(tmp_path)
    assert len(artifacts) == 5
    assert all(path.exists() for path in artifacts)


def test_placeholder_branches_when_no_samples(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(dry_run, "SAMPLE_ARTIFACTS", {})

    research = tmp_path / "research_pack.json"
    _create_dry_run_artifact(tmp_path, "research_pack", research)
    assert json.loads(research.read_text(encoding="utf-8"))["topic"]

    review = tmp_path / "review_report.json"
    _create_dry_run_artifact(tmp_path, "review_report", review)
    assert json.loads(review.read_text(encoding="utf-8"))["approved"] is True

    manuscript = tmp_path / "manuscript.md"
    _create_dry_run_artifact(tmp_path, "manuscript", manuscript)
    assert manuscript.read_text(encoding="utf-8").startswith("#")


def test_missing_required_sample_raises_clear_error(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(dry_run, "SAMPLE_ARTIFACTS", {})
    for artifact in ("book_plan", "latex_spec"):
        with pytest.raises(FileNotFoundError, match=artifact):
            _create_dry_run_artifact(tmp_path, artifact, tmp_path / f"{artifact}.json")
