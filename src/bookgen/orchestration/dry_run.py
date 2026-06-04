"""Dry-run artifact synthesis: create or reuse intermediate artifacts.

The dry-run path copies committed ``sample_*`` artifacts into the generated
runtime directory (or writes minimal placeholders) so the deterministic pipeline
runs end-to-end without an API key.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from bookgen.shared.config import project_root

EXPECTED_ARTIFACTS = {
    "book_plan": Path("generated/intermediate/book_plan.json"),
    "research_pack": Path("generated/intermediate/research_pack.json"),
    "manuscript": Path("generated/intermediate/manuscript.md"),
    "review_report": Path("generated/intermediate/review_report.json"),
    "latex_spec": Path("generated/intermediate/latex_spec.json"),
}

SAMPLE_ARTIFACTS = {
    "book_plan": Path("data/intermediate/sample_book_plan.json"),
    "research_pack": Path("data/intermediate/sample_research_pack.json"),
    "manuscript": Path("data/intermediate/sample_manuscript.md"),
    "review_report": Path("data/intermediate/sample_review_report.json"),
    "latex_spec": Path("data/intermediate/sample_latex_spec.json"),
}


def create_or_reuse_dry_run_artifacts(root_dir: Path | str) -> list[Path]:
    """Create or reuse the expected generated artifacts for dry-run mode."""
    root = Path(root_dir)
    (root / "generated/intermediate").mkdir(parents=True, exist_ok=True)

    created_or_existing: list[Path] = []
    for artifact_name, relative_path in EXPECTED_ARTIFACTS.items():
        target = root / relative_path
        if not target.exists():
            _create_dry_run_artifact(root, artifact_name, target)
        created_or_existing.append(target)
    return created_or_existing


def _create_dry_run_artifact(root: Path, artifact_name: str, target: Path) -> None:
    sample_path = SAMPLE_ARTIFACTS.get(artifact_name)
    if sample_path is not None:
        for sample_root in (root, project_root()):
            source = sample_root / sample_path
            if source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                return

    target.parent.mkdir(parents=True, exist_ok=True)
    if artifact_name == "research_pack":
        target.write_text(json.dumps(_sample_research_pack(), indent=2), encoding="utf-8")
    elif artifact_name == "review_report":
        target.write_text(json.dumps(_sample_review_report(), indent=2), encoding="utf-8")
    elif artifact_name == "manuscript":
        target.write_text(
            "# Dry Run Manuscript\n\nNo real CrewAI execution has happened.\n", encoding="utf-8"
        )
    else:
        target.write_text("{}", encoding="utf-8")


def _sample_research_pack() -> dict[str, Any]:
    return {
        "topic": "AI Agent Orchestration: From Prompting to Production-Ready Crews",
        "key_concepts": ["Agent", "Task", "Crew", "Process", "Context", "Harness"],
        "terminology": {
            "CrewAI": "Framework for role-based agent teams.",
            "Harness": "Deterministic software wrapper around model reasoning.",
        },
        "source_candidates": [
            {
                "source_id": "crewai_docs",
                "title": "CrewAI Documentation",
                "url": "https://docs.crewai.com/",
                "notes": "Reference source for CrewAI concepts.",
            }
        ],
        "chapter_notes": {"From Prompt To Crew": "Explain why specialized agents improve clarity."},
        "unsupported_claim_warnings": [],
    }


def _sample_review_report() -> dict[str, Any]:
    return {
        "approved": True,
        "checklist": {
            "cover": True,
            "toc": True,
            "chapters": True,
            "citations": True,
            "image": True,
            "graph": True,
            "table": True,
            "formula": True,
            "hebrew_english_section": True,
        },
        "notes": ["Dry-run artifact created without CrewAI kickoff."],
        "required_fixes": [],
    }
