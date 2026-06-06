"""Persist real CrewAI task outputs without poisoning canonical artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from bookgen.document.schemas import BookPlan, LatexSpec, ResearchPack, ReviewReport
from bookgen.orchestration.artifact_normalization import normalize_artifact_payload
from bookgen.shared.constants import ARTIFACT_NAMES, GENERATED_ARTIFACTS

SCHEMA_BY_ARTIFACT = {
    "book_plan": BookPlan,
    "research_pack": ResearchPack,
    "review_report": ReviewReport,
    "latex_spec": LatexSpec,
}


@dataclass(frozen=True)
class PersistedOutput:
    """Record describing one persisted real-run task output."""

    task: str
    raw_path: Path
    artifact_path: Path | None
    valid: bool
    error: str | None
    preview: str

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable trace record."""
        return {
            "task": self.task,
            "raw_path": str(self.raw_path),
            "artifact_path": str(self.artifact_path) if self.artifact_path else None,
            "valid": self.valid,
            "error": self.error,
            "preview": self.preview,
        }


def persist_task_outputs(result: Any, root: Path) -> tuple[list[dict[str, Any]], list[Path]]:
    """Persist raw real outputs and validated canonical artifacts when possible."""
    task_outputs = list(getattr(result, "tasks_output", []) or [])
    if not task_outputs:
        return _persist_single_output(result, root)

    records: list[dict[str, Any]] = []
    artifacts: list[Path] = []
    for name, output in zip(ARTIFACT_NAMES, task_outputs, strict=False):
        record = _persist_named_output(name, output, root)
        records.append(record.as_dict())
        artifacts.append(record.raw_path)
        if record.artifact_path:
            artifacts.append(record.artifact_path)
    return records, artifacts


def output_text(output: Any) -> str:
    raw = getattr(output, "raw", None)
    return raw if isinstance(raw, str) else str(output)


def preview(output: Any, limit: int = 240) -> str:
    return output_text(output).replace("\n", " ")[:limit]


def _persist_single_output(result: Any, root: Path) -> tuple[list[dict[str, Any]], list[Path]]:
    output_path = root / "generated/intermediate/real_run_output.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text(result), encoding="utf-8")
    return (
        [
            {
                "task": "crew",
                "raw_path": str(output_path),
                "artifact_path": None,
                "valid": True,
                "error": None,
                "preview": preview(result),
            }
        ],
        [output_path],
    )


def _persist_named_output(name: str, output: Any, root: Path) -> PersistedOutput:
    raw_path = _raw_output_path(root, name)
    text = output_text(output)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(text, encoding="utf-8")

    artifact_path = root / GENERATED_ARTIFACTS[name]
    error = _write_valid_artifact(name, text, artifact_path)
    return PersistedOutput(
        task=name,
        raw_path=raw_path,
        artifact_path=None if error else artifact_path,
        valid=error is None,
        error=error,
        preview=preview(output),
    )


def _raw_output_path(root: Path, name: str) -> Path:
    suffix = ".md" if name == "manuscript" else ".txt"
    return root / "generated/intermediate/real_raw" / f"{name}{suffix}"


def _write_valid_artifact(name: str, text: str, artifact_path: Path) -> str | None:
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    if name == "manuscript":
        if not text.strip():
            return "manuscript output is empty"
        artifact_path.write_text(text, encoding="utf-8")
        return None

    schema = SCHEMA_BY_ARTIFACT.get(name)
    if schema is None:
        return f"no schema registered for {name}"
    try:
        payload = json.loads(_extract_json_payload(text))
        if not isinstance(payload, dict):
            raise ValueError("JSON artifact must be an object")
        model = schema.model_validate(normalize_artifact_payload(name, payload))
    except (ValidationError, ValueError) as exc:
        return str(exc).splitlines()[0]
    artifact_path.write_text(model.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return None


def _extract_json_payload(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].lstrip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object found in output")
    return stripped[start : end + 1]
