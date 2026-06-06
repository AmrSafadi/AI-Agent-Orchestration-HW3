"""Tests for real-run persistence and accounting helpers."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from bookgen.orchestration.real_run import extract_token_usage, persist_real_run
from bookgen.shared.config import BudgetsConfig

FEATURES = {
    "cover",
    "toc",
    "image",
    "graph",
    "table",
    "formula",
    "hebrew_english_section",
    "citations",
}


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
        SimpleNamespace(raw=f"```json\n{json.dumps(_book_plan())}\n```"),
        SimpleNamespace(
            raw="""```json
{
  "topic": "Research",
  "key_concepts": ["Agent"],
  "terminology": {},
  "source_candidates": [],
  "chapter_notes": {},
  "unsupported_claim_warnings": []
}
```"""
        ),
        SimpleNamespace(raw=_manuscript()),
        SimpleNamespace(raw='```json\n{"approved": true}\n```'),
        SimpleNamespace(raw=f"```json\n{json.dumps(_latex_spec())}\n```"),
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


def _book_plan() -> dict:
    return {
        "title": "Plan",
        "audience": "Reviewer",
        "chapters": [
            {
                "title": f"Chapter {index}",
                "summary": "Summary",
                "sections": [{"title": "Why", "purpose": "Explain why."}],
            }
            for index in range(1, 6)
        ],
        "required_feature_placement": dict.fromkeys(FEATURES, "Chapter 1"),
        "acceptance_checklist": sorted(FEATURES),
        "estimated_pages": 16,
    }


def _manuscript() -> str:
    hebrew_word = "\u05e1\u05d5\u05db\u05df"
    chapters = []
    for index in range(1, 6):
        body = " ".join([hebrew_word] * 330)
        chapters.append(
            f"## Chapter {index}\n\n"
            f"### Section {index}\n\n"
            f"{body} Agent Task Crew Harness validation [@crewai_docs]."
        )
    return "# AI Agent Orchestration\n\n" + "\n\n".join(chapters)


def _latex_spec() -> dict:
    return {
        "title": "Spec",
        "engine": "lualatex",
        "main_template": "main.tex.j2",
        "output_pdf": "generated/pdf/final.pdf",
        "chapter_files": ["chapters/chapter_01.tex"],
        "assets": [
            _asset("img", "image"),
            _asset("graph", "graph"),
            _asset("table", "table"),
            _asset("formula", "formula"),
        ],
        "bibliography_file": "data/references/references.bib",
    }


def _asset(asset_id: str, kind: str) -> dict:
    return {
        "asset_id": asset_id,
        "kind": kind,
        "target_path": f"generated/assets/{kind}.png",
        "caption": kind,
    }
