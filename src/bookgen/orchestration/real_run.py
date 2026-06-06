"""Persistence, token accounting, and budget checks for opt-in real crew runs."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bookgen.orchestration.accounting import budget_alerts, extract_token_usage
from bookgen.shared.config import BudgetsConfig
from bookgen.shared.constants import ARTIFACT_NAMES, GENERATED_ARTIFACTS

TRACE_PATH = Path("generated/intermediate/real_run_trace.json")
SUMMARY_PATH = Path("generated/intermediate/real_run_summary.json")


@dataclass(frozen=True)
class RealRunSummary:
    """Artifacts and accounting data captured from a real CrewAI run."""

    artifacts: list[Path]
    token_usage: dict[str, int | float]
    budget_alerts: list[str]


def persist_real_run(
    result: Any,
    root_dir: Path | str,
    inputs: dict[str, Any],
    budgets: BudgetsConfig,
) -> RealRunSummary:
    """Persist task outputs, token usage, and budget warnings for a real run."""
    root = Path(root_dir)
    intermediate = root / "generated/intermediate"
    intermediate.mkdir(parents=True, exist_ok=True)

    task_records, artifacts = _persist_task_outputs(result, root)
    token_usage = extract_token_usage(result)
    alerts = budget_alerts(token_usage, budgets)
    trace = {
        "mode": "real",
        "inputs": inputs,
        "task_outputs": task_records,
        "token_usage": token_usage,
        "budget_alerts": alerts,
    }
    trace_path = root / TRACE_PATH
    summary_path = root / SUMMARY_PATH
    _write_json(trace_path, trace)
    _write_json(summary_path, _summary_payload(result, token_usage, alerts, artifacts))

    logger = logging.getLogger("bookgen.real_run")
    for record in task_records:
        logger.info("real task output persisted: %s", record["artifact_path"])
    for alert in alerts:
        logger.warning("budget alert: %s", alert)
    return RealRunSummary([*artifacts, trace_path, summary_path], token_usage, alerts)


def _persist_task_outputs(result: Any, root: Path) -> tuple[list[dict[str, Any]], list[Path]]:
    task_outputs = list(getattr(result, "tasks_output", []) or [])
    if not task_outputs:
        output_path = root / "generated/intermediate/real_run_output.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(_output_text(result), encoding="utf-8")
        return (
            [{"task": "crew", "artifact_path": str(output_path), "preview": _preview(result)}],
            [output_path],
        )

    records: list[dict[str, Any]] = []
    artifacts: list[Path] = []
    for name, output in zip(ARTIFACT_NAMES, task_outputs, strict=False):
        artifact_path = root / GENERATED_ARTIFACTS[name]
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(_output_text(output), encoding="utf-8")
        artifacts.append(artifact_path)
        records.append(
            {"task": name, "artifact_path": str(artifact_path), "preview": _preview(output)}
        )
    return records, artifacts


def _output_text(output: Any) -> str:
    raw = getattr(output, "raw", None)
    return raw if isinstance(raw, str) else str(output)


def _preview(output: Any, limit: int = 240) -> str:
    return _output_text(output).replace("\n", " ")[:limit]


def _summary_payload(
    result: Any,
    token_usage: dict[str, int | float],
    alerts: list[str],
    artifacts: list[Path],
) -> dict[str, Any]:
    return {
        "mode": "real",
        "output_preview": _preview(result),
        "artifacts": [str(path) for path in artifacts],
        "token_usage": token_usage,
        "budget_alerts": alerts,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
