"""Deterministic document validation helpers (artifacts, project, spec files).

Required-feature validation lives in ``document_features`` and is re-exported here.
"""

from __future__ import annotations

from pathlib import Path

from bookgen.document.document_features import (
    report_from_checks,
    validate_required_document_features,
)
from bookgen.document.schemas import LatexSpec, ValidationCheck, ValidationReport
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
    return report_from_checks(checks)


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
    return report_from_checks(checks)


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
    return report_from_checks(checks)
