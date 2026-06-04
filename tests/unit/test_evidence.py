"""Tests for the final evidence report builder and writer."""

from __future__ import annotations

from pathlib import Path

from bookgen.document.schemas import ValidationCheck, ValidationReport
from bookgen.harness.evidence import build_evidence_report, write_final_report


def _validation() -> ValidationReport:
    return ValidationReport(
        passed=True,
        checks=[
            ValidationCheck(name="feature:cover", passed=True),
            ValidationCheck(name="feature:table", passed=False),
            ValidationCheck(name="artifact:book_plan", passed=True),
        ],
    )


def test_build_evidence_report_extracts_feature_checklist() -> None:
    report = build_evidence_report(
        _validation(), pdf_path="generated/pdf/final.pdf", build_passed=True
    )
    assert report.validation_passed is True
    assert report.build_passed is True
    assert report.requirement_checklist == {"feature:cover": True, "feature:table": False}


def test_write_final_report_emits_markdown(tmp_path: Path) -> None:
    report = build_evidence_report(_validation(), limitations=["no PDF yet"])
    out = write_final_report(report, tmp_path / "final_report.md")
    text = out.read_text(encoding="utf-8")
    assert "# Final Evidence Report" in text
    assert "feature:cover" in text
    assert "no PDF yet" in text
