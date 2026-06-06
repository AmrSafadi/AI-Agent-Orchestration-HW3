"""Persistence, token accounting, and budget checks for opt-in real crew runs."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bookgen.orchestration.accounting import budget_alerts, extract_token_usage
from bookgen.orchestration.artifact_persistence import persist_task_outputs, preview
from bookgen.shared.config import BudgetsConfig

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

    task_records, artifacts = persist_task_outputs(result, root)
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
        _log_persisted_output(logger, record)
    for alert in alerts:
        logger.warning("budget alert: %s", alert)
    return RealRunSummary([*artifacts, trace_path, summary_path], token_usage, alerts)


def _summary_payload(
    result: Any,
    token_usage: dict[str, int | float],
    alerts: list[str],
    artifacts: list[Path],
) -> dict[str, Any]:
    return {
        "mode": "real",
        "output_preview": preview(result),
        "artifacts": [str(path) for path in artifacts],
        "token_usage": token_usage,
        "budget_alerts": alerts,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _log_persisted_output(logger: logging.Logger, record: dict[str, Any]) -> None:
    task = record["task"]
    if record["valid"]:
        logger.info("real task output accepted for %s: %s", task, record["artifact_path"])
        return
    logger.info(
        "real task output saved raw for %s; canonical artifact unchanged: %s (raw: %s)",
        task,
        record["error"],
        record["raw_path"],
    )
