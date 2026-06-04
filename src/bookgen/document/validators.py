"""Deterministic document validation helpers."""

from __future__ import annotations

from pathlib import Path

from bookgen.document.schemas import BookPlan, LatexSpec, ValidationCheck, ValidationReport
from bookgen.harness.citations import extract_citation_keys
from bookgen.shared.constants import GENERATED_ARTIFACTS, REQUIRED_FEATURES

__all__ = [
    "REQUIRED_ARTIFACTS",
    "REQUIRED_FEATURES",
    "validate_required_artifacts",
    "validate_required_document_features",
    "validate_project",
    "validate_latex_spec_files",
]

# Derived from the shared artifact map so this list cannot drift from the
# dry-run synthesizer (see bookgen.shared.constants).
REQUIRED_ARTIFACTS = tuple(str(path) for path in GENERATED_ARTIFACTS.values())


def validate_required_artifacts(root_dir: Path | str = ".") -> ValidationReport:
    """Validate that required runtime intermediate artifacts exist."""
    root = Path(root_dir)
    checks = [
        ValidationCheck(
            name=f"artifact:{relative_path}",
            passed=(root / relative_path).exists(),
            message=str(root / relative_path),
        )
        for relative_path in REQUIRED_ARTIFACTS
    ]
    return _report_from_checks(checks)


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

    return _report_from_checks(checks)


def validate_project(
    root_dir: Path | str = ".",
    book_plan_path: Path | str | None = None,
    latex_spec_path: Path | str | None = None,
    manuscript_path: Path | str | None = None,
) -> ValidationReport:
    """Validate required artifacts and, when present, required document features."""
    root = Path(root_dir)
    artifact_report = validate_required_artifacts(root)

    plan = (
        Path(book_plan_path) if book_plan_path else root / "generated/intermediate/book_plan.json"
    )
    spec = (
        Path(latex_spec_path)
        if latex_spec_path
        else root / "generated/intermediate/latex_spec.json"
    )
    manuscript = (
        Path(manuscript_path) if manuscript_path else root / "generated/intermediate/manuscript.md"
    )

    if not (plan.exists() and spec.exists() and manuscript.exists()):
        return artifact_report

    feature_report = validate_required_document_features(plan, spec, manuscript)
    checks = [*artifact_report.checks, *feature_report.checks]
    return _report_from_checks(checks)


def validate_latex_spec_files(
    latex_spec_path: Path | str,
    root_dir: Path | str = ".",
) -> ValidationReport:
    """Validate that files referenced by the LaTeX spec actually exist on disk."""
    root = Path(root_dir)
    latex_spec = LatexSpec.model_validate_json(Path(latex_spec_path).read_text(encoding="utf-8"))
    references = [asset.target_path for asset in latex_spec.assets]
    references.append(latex_spec.bibliography_file)
    checks = [
        ValidationCheck(
            name=f"file:{reference}",
            passed=(root / reference).exists(),
            message=str(root / reference),
        )
        for reference in references
    ]
    return _report_from_checks(checks)


def _report_from_checks(checks: list[ValidationCheck]) -> ValidationReport:
    errors = [f"{check.name}: {check.message}" for check in checks if not check.passed]
    return ValidationReport(passed=not errors, checks=checks, errors=errors)


def _contains_hebrew(text: str) -> bool:
    return any("\u0590" <= character <= "\u05ff" for character in text)


def _contains_latin(text: str) -> bool:
    return any(("a" <= character.lower() <= "z") for character in text)
