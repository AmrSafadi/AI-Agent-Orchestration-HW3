"""Validate a raw real-run task output and write the canonical artifact.

Split out of ``artifact_persistence`` (guideline 3.2): this module owns the
schema-validation + content-quality-gate + write concern, leaving
``artifact_persistence`` to own raw-output persistence and orchestration. It
does not import ``artifact_persistence``, so there is no import cycle.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from bookgen.document.content_quality import artifact_quality_error
from bookgen.document.schemas import BookPlan, LatexSpec, ResearchPack, ReviewReport
from bookgen.orchestration.artifact_normalization import normalize_artifact_payload
from bookgen.orchestration.artifact_normalization_utils import extract_json_payload

SCHEMA_BY_ARTIFACT = {
    "book_plan": BookPlan,
    "research_pack": ResearchPack,
    "review_report": ReviewReport,
    "latex_spec": LatexSpec,
}


def write_valid_artifact(name: str, text: str, artifact_path: Path) -> str | None:
    """Validate ``text`` for ``name`` and write the canonical artifact.

    Returns ``None`` on success, or a one-line error string when the output
    fails schema validation or the content-quality gate (the caller then keeps
    the raw output and leaves the canonical artifact untouched).
    """
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    if name == "manuscript":
        if not text.strip():
            return "manuscript output is empty"
        quality_error = artifact_quality_error(name, text)
        if quality_error:
            return quality_error
        artifact_path.write_text(text, encoding="utf-8")
        return None

    schema = SCHEMA_BY_ARTIFACT.get(name)
    if schema is None:
        return f"no schema registered for {name}"
    try:
        payload = json.loads(extract_json_payload(text))
        if not isinstance(payload, dict):
            raise ValueError("JSON artifact must be an object")
        model = schema.model_validate(normalize_artifact_payload(name, payload))
        quality_error = artifact_quality_error(name, model)
        if quality_error:
            return quality_error
    except (ValidationError, ValueError) as exc:
        return str(exc).splitlines()[0]
    artifact_path.write_text(model.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return None
