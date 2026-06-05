"""Required-document-feature validation (cover/TOC/citations/BiDi/assets/...).

Split out of ``validators.py`` to keep each module within the 150-line limit.
``validators.py`` re-exports ``validate_required_document_features`` and reuses
``report_from_checks`` here.
"""

from __future__ import annotations

from pathlib import Path

from bookgen.document.schemas import BookPlan, LatexSpec, ValidationCheck, ValidationReport
from bookgen.harness.citations import extract_citation_keys


def report_from_checks(checks: list[ValidationCheck]) -> ValidationReport:
    """Build a ValidationReport, collecting failing-check messages as errors."""
    errors = [f"{check.name}: {check.message}" for check in checks if not check.passed]
    return ValidationReport(passed=not errors, checks=checks, errors=errors)


def validate_required_document_features(
    book_plan_path: Path | str,
    latex_spec_path: Path | str,
    manuscript_path: Path | str,
) -> ValidationReport:
    """Validate required document features from plan/spec/manuscript artifacts."""
    book_plan = BookPlan.model_validate_json(Path(book_plan_path).read_text(encoding="utf-8"))
    latex_spec = LatexSpec.model_validate_json(Path(latex_spec_path).read_text(encoding="utf-8"))
    manuscript_text = Path(manuscript_path).read_text(encoding="utf-8")

    feature_placements = {key.lower() for key in book_plan.required_feature_placement}
    asset_kinds = {asset.kind for asset in latex_spec.assets}

    checks = [
        ValidationCheck(
            name="feature:cover",
            passed=bool(book_plan.title and book_plan.audience and "cover" in feature_placements),
            message="Book plan must include cover placement and metadata.",
        ),
        ValidationCheck(
            name="feature:toc",
            passed="toc" in feature_placements,
            message="Book plan must include table-of-contents placement.",
        ),
        ValidationCheck(
            name="feature:chapters",
            passed=bool(book_plan.chapters),
            message="Book plan must include at least one chapter.",
        ),
        ValidationCheck(
            name="feature:citations",
            passed=bool(extract_citation_keys(manuscript_text)),
            message="Manuscript must include at least one citation marker.",
        ),
        ValidationCheck(
            name="feature:image",
            passed="image" in asset_kinds,
            message="LaTeX spec must include at least one image asset.",
        ),
        ValidationCheck(
            name="feature:graph",
            passed="graph" in asset_kinds,
            message="LaTeX spec must include the Python-generated graph asset.",
        ),
        ValidationCheck(
            name="feature:table",
            passed="table" in asset_kinds,
            message="LaTeX spec must include at least one table asset.",
        ),
        ValidationCheck(
            name="feature:formula",
            passed="formula" in asset_kinds,
            message="LaTeX spec must include at least one formula asset.",
        ),
        ValidationCheck(
            name="feature:hebrew_english_section",
            passed=_contains_hebrew(manuscript_text) and _contains_latin(manuscript_text),
            message="Manuscript must include mixed Hebrew-English text.",
        ),
    ]

    return report_from_checks(checks)


def _contains_hebrew(text: str) -> bool:
    return any("֐" <= character <= "׿" for character in text)


def _contains_latin(text: str) -> bool:
    return any(("a" <= character.lower() <= "z") for character in text)
