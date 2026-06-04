"""Edge-case and pass-path tests for the document validators."""

from __future__ import annotations

import json
from pathlib import Path

from bookgen.document.validators import (
    REQUIRED_ARTIFACTS,
    validate_project,
    validate_required_artifacts,
    validate_required_document_features,
)


def test_required_artifacts_missing_then_present(tmp_path: Path) -> None:
    report = validate_required_artifacts(tmp_path)
    assert not report.passed
    assert len(report.errors) == len(REQUIRED_ARTIFACTS)

    for relative_path in REQUIRED_ARTIFACTS:
        target = tmp_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}", encoding="utf-8")

    report_after = validate_required_artifacts(tmp_path)
    assert report_after.passed
    assert report_after.errors == []


def test_all_features_pass(
    write_features, default_book_plan, default_latex_spec, default_manuscript
) -> None:
    paths = write_features(default_book_plan, default_latex_spec, default_manuscript)
    report = validate_required_document_features(*paths)
    assert report.passed, report.errors


def test_missing_cover_toc_and_citation_fail(
    write_features, default_book_plan, default_latex_spec
) -> None:
    plan = {**default_book_plan, "required_feature_placement": {}}
    manuscript = "מערכת plain English text without any citation marker."
    paths = write_features(plan, default_latex_spec, manuscript)
    report = validate_required_document_features(*paths)
    assert not report.passed
    assert any("feature:cover" in error for error in report.errors)
    assert any("feature:toc" in error for error in report.errors)
    assert any("feature:citations" in error for error in report.errors)


def test_english_only_manuscript_fails_bidi(
    write_features, default_book_plan, default_latex_spec
) -> None:
    paths = write_features(default_book_plan, default_latex_spec, "English only [@crewai_docs].")
    report = validate_required_document_features(*paths)
    assert any("feature:hebrew_english_section" in error for error in report.errors)


def test_validate_project_returns_artifact_report_when_incomplete(tmp_path: Path) -> None:
    report = validate_project(tmp_path)
    assert not report.passed
    assert all(check.name.startswith("artifact:") for check in report.checks)


def test_validate_project_merges_feature_checks(
    tmp_path: Path, default_book_plan, default_latex_spec, default_manuscript
) -> None:
    intermediate = tmp_path / "generated/intermediate"
    intermediate.mkdir(parents=True, exist_ok=True)
    (intermediate / "book_plan.json").write_text(json.dumps(default_book_plan), encoding="utf-8")
    (intermediate / "research_pack.json").write_text("{}", encoding="utf-8")
    (intermediate / "manuscript.md").write_text(default_manuscript, encoding="utf-8")
    (intermediate / "review_report.json").write_text("{}", encoding="utf-8")
    (intermediate / "latex_spec.json").write_text(json.dumps(default_latex_spec), encoding="utf-8")

    report = validate_project(tmp_path)
    assert report.passed, report.errors
    assert any(check.name.startswith("feature:") for check in report.checks)
    assert any(check.name.startswith("artifact:") for check in report.checks)
