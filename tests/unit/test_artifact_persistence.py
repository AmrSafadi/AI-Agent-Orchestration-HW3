"""Tests for safe real-run artifact persistence."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from bookgen.orchestration.artifact_persistence import persist_task_outputs

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


def test_valid_fenced_json_replaces_canonical_artifact(tmp_path: Path) -> None:
    payload = json.dumps(_strong_book_plan("Plan"))
    output = SimpleNamespace(
        raw=f"""```json
{payload}
```"""
    )

    records, artifacts = persist_task_outputs(SimpleNamespace(tasks_output=[output]), tmp_path)

    artifact_path = tmp_path / "generated/intermediate/book_plan.json"
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["title"] == "Plan"
    assert records[0]["valid"] is True
    assert artifact_path in artifacts


def test_invalid_json_schema_keeps_existing_canonical_artifact(tmp_path: Path) -> None:
    artifact_path = tmp_path / "generated/intermediate/book_plan.json"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text('{"existing": true}', encoding="utf-8")
    output = SimpleNamespace(raw='```json\n{"chapterOutline": []}\n```')

    records, artifacts = persist_task_outputs(SimpleNamespace(tasks_output=[output]), tmp_path)

    assert artifact_path.read_text(encoding="utf-8") == '{"existing": true}'
    assert records[0]["valid"] is False
    assert "validation errors for BookPlan" in records[0]["error"]
    assert tmp_path / "generated/intermediate/real_raw/book_plan.txt" in artifacts
    assert artifact_path not in artifacts


def test_quality_gate_keeps_shallow_manuscript_out_of_canonical(tmp_path: Path) -> None:
    outputs = [
        SimpleNamespace(raw=json.dumps(_strong_book_plan())),
        SimpleNamespace(raw=json.dumps(_research_pack())),
        SimpleNamespace(raw="# Manuscript\n\nDraft with Citation Placeholder."),
    ]

    records, artifacts = persist_task_outputs(SimpleNamespace(tasks_output=outputs), tmp_path)

    assert records[2]["valid"] is False
    assert "placeholder" in records[2]["error"]
    assert tmp_path / "generated/intermediate/manuscript.md" not in artifacts
    assert (tmp_path / "generated/intermediate/real_raw/manuscript.md").exists()


def _strong_book_plan(title: str = "AI Agent Orchestration") -> dict:
    return {
        "title": title,
        "audience": "Course evaluator",
        "chapters": [
            {
                "title": f"Chapter {index}",
                "summary": "Submission-ready chapter.",
                "sections": [{"title": "Section", "purpose": "Explain a concrete idea."}],
            }
            for index in range(1, 6)
        ],
        "required_feature_placement": dict.fromkeys(FEATURES, "Chapter 1"),
        "acceptance_checklist": sorted(FEATURES),
        "estimated_pages": 16,
    }


def _research_pack() -> dict:
    return {
        "topic": "AI Agent Orchestration",
        "key_concepts": ["Agent"],
        "source_candidates": [{"source_id": "crewai_docs", "title": "CrewAI", "notes": ""}],
        "chapter_notes": {"Chapter 1": "Use CrewAI docs."},
    }
