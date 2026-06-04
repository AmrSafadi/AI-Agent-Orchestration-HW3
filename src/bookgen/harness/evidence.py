"""Build and persist the final evidence report for a generation run."""

from __future__ import annotations

from pathlib import Path

from bookgen.document.report_schemas import EvidenceReport
from bookgen.document.schemas import ValidationReport

DEFAULT_EVIDENCE_PATH = Path("generated/reports/final_report.md")


def build_evidence_report(
    validation_report: ValidationReport,
    pdf_path: str | None = None,
    build_passed: bool = False,
    token_summary: dict[str, int] | None = None,
    limitations: list[str] | None = None,
) -> EvidenceReport:
    """Aggregate run results into a structured EvidenceReport."""
    checklist = {
        check.name: check.passed
        for check in validation_report.checks
        if check.name.startswith("feature:")
    }
    return EvidenceReport(
        pdf_path=pdf_path,
        build_passed=build_passed,
        validation_passed=validation_report.passed,
        requirement_checklist=checklist,
        token_summary=token_summary,
        limitations=limitations or [],
    )


def write_final_report(
    report: EvidenceReport,
    output_path: Path | str = DEFAULT_EVIDENCE_PATH,
) -> Path:
    """Render the evidence report as a Markdown file and return its path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Final Evidence Report",
        "",
        f"- PDF: {report.pdf_path or 'not generated'}",
        f"- Build passed: {report.build_passed}",
        f"- Validation passed: {report.validation_passed}",
        "",
        "## Requirement checklist",
    ]
    if report.requirement_checklist:
        lines += [
            f"- [{'x' if passed else ' '}] {name}"
            for name, passed in sorted(report.requirement_checklist.items())
        ]
    else:
        lines.append("- (no feature checks recorded)")
    if report.limitations:
        lines += ["", "## Known limitations", *(f"- {item}" for item in report.limitations)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
