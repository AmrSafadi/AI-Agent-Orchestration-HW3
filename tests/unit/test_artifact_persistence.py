"""Tests for safe real-run artifact persistence."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from bookgen.orchestration.artifact_persistence import persist_task_outputs


def test_valid_fenced_json_replaces_canonical_artifact(tmp_path: Path) -> None:
    output = SimpleNamespace(
        raw="""```json
{
  "title": "Plan",
  "audience": "Reviewer",
  "chapters": [
    {
      "title": "Intro",
      "summary": "Summary",
      "sections": [{"title": "Why", "purpose": "Explain why."}]
    }
  ],
  "acceptance_checklist": ["cover"],
  "estimated_pages": 1
}
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


def test_common_real_output_variants_are_normalized(tmp_path: Path) -> None:
    outputs = [
        SimpleNamespace(
            raw=json.dumps(
                {
                    "title": "AI Agent Orchestration",
                    "audience": {"primary": "Students"},
                    "chapterOutline": [{"chapterTitle": "Intro", "sections": ["Agents", "Tasks"]}],
                    "requiredFeaturePlacement": {"callouts": ["Chapter 1"]},
                    "acceptanceChecklist": ["cover"],
                    "estimatedPageCount": 16,
                }
            )
        ),
        SimpleNamespace(
            raw=json.dumps(
                {
                    "title": "AI Agent Orchestration",
                    "chapters": [
                        {
                            "chapterTitle": "Intro",
                            "keyConcepts": ["Agent"],
                            "terminology": {"Agent": "Role-bound worker"},
                            "sourceCandidates": ["CrewAI docs"],
                            "chapterNotes": {"Agents": "Explain roles."},
                            "unsupportedClaimWarnings": ["Avoid unsupported claims."],
                        }
                    ],
                }
            )
        ),
        SimpleNamespace(raw="# Manuscript\n\nDraft."),
        SimpleNamespace(
            raw=json.dumps(
                {
                    "approval_status": "pending",
                    "checklist_results": {"cover": True},
                    "notes": {"clarity": "Good"},
                    "required_fixes": {"citations": ["Add citations"]},
                }
            )
        ),
        SimpleNamespace(
            raw=json.dumps(
                {
                    "template": "book_template.tex",
                    "chapter_files": ["chapters/chapter1.tex"],
                    "asset_references": {
                        "figures": [
                            "generated/assets/images/course_concept_image.png",
                            "generated/assets/graphs/agent_pipeline_graph.png",
                        ]
                    },
                    "bibliography_file": "references.bib",
                    "output_pdf_path": "generated/pdf/final.pdf",
                    "engine": "pdflatex",
                    "bidi_settings": {"use_bidi": True},
                }
            )
        ),
    ]

    records, _ = persist_task_outputs(SimpleNamespace(tasks_output=outputs), tmp_path)

    assert [record["valid"] for record in records] == [True, True, True, True, True]
    book_plan = json.loads(
        (tmp_path / "generated/intermediate/book_plan.json").read_text(encoding="utf-8")
    )
    research_pack = json.loads(
        (tmp_path / "generated/intermediate/research_pack.json").read_text(encoding="utf-8")
    )
    review_report = json.loads(
        (tmp_path / "generated/intermediate/review_report.json").read_text(encoding="utf-8")
    )
    latex_spec = json.loads(
        (tmp_path / "generated/intermediate/latex_spec.json").read_text(encoding="utf-8")
    )
    assert book_plan["chapters"][0]["title"] == "Intro"
    assert research_pack["source_candidates"][0]["source_id"] == "crewai_docs"
    assert review_report["notes"] == ["clarity: Good"]
    assert latex_spec["engine"] == "lualatex"
