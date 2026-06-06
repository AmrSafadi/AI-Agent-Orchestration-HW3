"""Tests for real-run artifact normalization (varied CrewAI output shapes)."""

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


def test_common_real_output_variants_are_normalized_when_content_is_strong(
    tmp_path: Path,
) -> None:
    outputs = [
        SimpleNamespace(
            raw=json.dumps(
                {
                    "title": "AI Agent Orchestration",
                    "audience": {"primary": "Students"},
                    "chapterOutline": [
                        {
                            "chapterTitle": f"Chapter {index}",
                            "sections": ["Agents", "Tasks"],
                        }
                        for index in range(1, 6)
                    ],
                    "requiredFeaturePlacement": dict.fromkeys(FEATURES, "Chapter 1"),
                    "acceptanceChecklist": sorted(FEATURES),
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
        SimpleNamespace(raw=_strong_manuscript()),
        SimpleNamespace(
            raw=json.dumps(
                {
                    "approval_status": "approved",
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
                    "assets": [
                        _asset("img", "image"),
                        _asset("graph", "graph"),
                        _asset("table", "table"),
                        _asset("formula", "formula"),
                    ],
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
    assert book_plan["chapters"][0]["title"] == "Chapter 1"
    assert research_pack["source_candidates"][0]["source_id"] == "crewai_docs"
    assert review_report["notes"] == ["clarity: Good"]
    assert latex_spec["engine"] == "lualatex"


def _strong_manuscript() -> str:
    hebrew_word = "סוכן"
    chapters = []
    for index in range(1, 6):
        body = " ".join([hebrew_word] * 330)
        chapters.append(
            f"## Chapter {index}\n\n"
            f"### Section {index}\n\n"
            f"{body} Agent Task Crew Harness validation [@crewai_docs]."
        )
    return "# AI Agent Orchestration\n\n" + "\n\n".join(chapters)


def _asset(asset_id: str, kind: str) -> dict:
    return {
        "asset_id": asset_id,
        "kind": kind,
        "target_path": f"generated/assets/{kind}.png",
        "caption": kind,
    }
