"""Tests for real-run persistence and accounting helpers."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from bookgen.orchestration.real_run import extract_token_usage, persist_real_run
from bookgen.shared.config import BudgetsConfig


def _budgets(max_tokens: int = 10) -> BudgetsConfig:
    return BudgetsConfig(
        version="1.00",
        max_total_usd=1.0,
        max_total_tokens=max_tokens,
        warn_at_percent=80,
    )


def test_extract_token_usage_from_crewai_like_result() -> None:
    result = SimpleNamespace(
        token_usage={"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20}
    )

    usage = extract_token_usage(result)

    assert usage["prompt_tokens"] == 12
    assert usage["completion_tokens"] == 8
    assert usage["total_tokens"] == 20


def test_persist_real_run_writes_task_outputs_and_budget_trace(tmp_path: Path) -> None:
    outputs = [
        SimpleNamespace(raw='{"title": "plan"}'),
        SimpleNamespace(raw='{"topic": "research"}'),
        SimpleNamespace(raw="# Manuscript"),
        SimpleNamespace(raw='{"approved": true}'),
        SimpleNamespace(raw='{"engine": "lualatex"}'),
    ]
    result = SimpleNamespace(tasks_output=outputs, token_usage={"total_tokens": 12})

    summary = persist_real_run(result, tmp_path, inputs={"topic": "x"}, budgets=_budgets())

    assert (
        (tmp_path / "generated/intermediate/book_plan.json")
        .read_text(encoding="utf-8")
        .startswith("{")
    )
    trace_path = tmp_path / "generated/intermediate/real_run_trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace["inputs"] == {"topic": "x"}
    assert trace["task_outputs"][0]["task"] == "book_plan"
    assert summary.token_usage["total_tokens"] == 12
    assert summary.budget_alerts
    assert trace_path in summary.artifacts
