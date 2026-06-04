"""Build and persist the deterministic citation reconciliation report."""

from __future__ import annotations

from pathlib import Path

from bookgen.document.report_schemas import CitationReport
from bookgen.harness.citations import (
    DEFAULT_BIB_PATH,
    DEFAULT_REGISTRY_PATH,
    validate_citation_keys,
)

DEFAULT_CITATION_REPORT_PATH = Path("generated/reports/citation_report.json")


def build_citation_report(
    manuscript_path: Path | str,
    registry_path: Path | str = DEFAULT_REGISTRY_PATH,
    bib_path: Path | str = DEFAULT_BIB_PATH,
) -> CitationReport:
    """Reconcile a manuscript's citations against the registry into a report."""
    result = validate_citation_keys(manuscript_path, registry_path)
    return CitationReport(
        bib_path=str(bib_path),
        used_keys=sorted(result.used_keys),
        known_keys=sorted(result.known_keys),
        missing_keys=sorted(result.missing_keys),
        unused_keys=sorted(result.unused_keys),
        passed=result.passed,
    )


def write_citation_report(
    report: CitationReport,
    output_path: Path | str = DEFAULT_CITATION_REPORT_PATH,
) -> Path:
    """Write the citation report as JSON and return its path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return path
