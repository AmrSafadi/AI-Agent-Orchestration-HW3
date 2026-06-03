"""CrewAI crew assembly with dry-run safety as the default behavior."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:  # pragma: no cover - exercised only when CrewAI is installed locally.
    from crewai import Crew as CrewAICrew
    from crewai import Process as CrewAIProcess
except ImportError:  # pragma: no cover - the fallback is covered by tests.
    CrewAICrew = None
    CrewAIProcess = None

from bookgen.orchestration.agents import create_all_agents
from bookgen.orchestration.tasks import create_all_tasks
from bookgen.shared.config import load_config, project_root

EXPECTED_ARTIFACTS = {
    "book_plan": Path("data/intermediate/book_plan.json"),
    "research_pack": Path("data/intermediate/research_pack.json"),
    "manuscript": Path("data/intermediate/manuscript.md"),
    "review_report": Path("data/intermediate/review_report.json"),
    "latex_spec": Path("data/intermediate/latex_spec.json"),
}

SAMPLE_ARTIFACTS = {
    "book_plan": Path("data/intermediate/sample_book_plan.json"),
    "manuscript": Path("data/intermediate/sample_manuscript.md"),
    "latex_spec": Path("data/intermediate/sample_latex_spec.json"),
}


@dataclass
class DryRunCrew:
    """Minimal Crew-compatible object used when CrewAI is unavailable."""

    agents: list[Any]
    tasks: list[Any]
    process: str = "sequential"
    verbose: bool = True


@dataclass
class CrewRunResult:
    """Result returned by ``run_crew``."""

    dry_run: bool
    message: str
    artifacts: list[Path]
    output: Any | None = None


def create_document_generation_crew(use_real_crewai: bool = False) -> Any:
    """Create the sequential CrewAI crew, or a dry-run-compatible crew object."""
    agents_by_name = create_all_agents(use_real_crewai=use_real_crewai)
    tasks = create_all_tasks(agents_by_name, use_real_crewai=use_real_crewai)
    agents = list(agents_by_name.values())

    if not use_real_crewai:
        return DryRunCrew(agents=agents, tasks=tasks)
    if CrewAICrew is None or CrewAIProcess is None:
        raise RuntimeError("CrewAI is not installed; real crew execution is unavailable.")

    return CrewAICrew(
        agents=agents,
        tasks=tasks,
        process=CrewAIProcess.sequential,
        verbose=True,
    )


def run_crew(dry_run: bool = True, root_dir: Path | str | None = None) -> CrewRunResult:
    """Run the crew safely.

    Dry-run is the default and never calls ``kickoff``. It creates or reuses the
    expected intermediate artifacts so later deterministic milestones can be
    tested without an API key.
    """
    root = Path(root_dir) if root_dir else project_root()

    if dry_run:
        artifacts = create_or_reuse_dry_run_artifacts(root)
        message = "Dry-run completed. CrewAI kickoff was not called."
        print(message)
        return CrewRunResult(dry_run=True, message=message, artifacts=artifacts)

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for real CrewAI execution.")

    crew = create_document_generation_crew(use_real_crewai=True)

    app_config = load_config(root / "config")
    result = crew.kickoff(inputs={"topic": app_config.setup.project.topic})
    message = "Real CrewAI execution completed."
    print(message)
    return CrewRunResult(dry_run=False, message=message, artifacts=[], output=result)


def create_or_reuse_dry_run_artifacts(root_dir: Path | str) -> list[Path]:
    """Create or reuse the expected intermediate artifacts for dry-run mode."""
    root = Path(root_dir)
    intermediate_dir = root / "data/intermediate"
    intermediate_dir.mkdir(parents=True, exist_ok=True)

    created_or_existing: list[Path] = []
    for artifact_name, relative_path in EXPECTED_ARTIFACTS.items():
        target = root / relative_path
        if not target.exists():
            _create_dry_run_artifact(root, artifact_name, target)
        created_or_existing.append(target)

    return created_or_existing


def _create_dry_run_artifact(root: Path, artifact_name: str, target: Path) -> None:
    sample_path = SAMPLE_ARTIFACTS.get(artifact_name)
    if sample_path is not None and (root / sample_path).exists():
        shutil.copyfile(root / sample_path, target)
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    if artifact_name == "research_pack":
        target.write_text(json.dumps(_sample_research_pack(), indent=2), encoding="utf-8")
    elif artifact_name == "review_report":
        target.write_text(json.dumps(_sample_review_report(), indent=2), encoding="utf-8")
    elif artifact_name == "manuscript":
        target.write_text("# Dry Run Manuscript\n\nNo real CrewAI execution has happened.\n", encoding="utf-8")
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
        "chapter_notes": {
            "From Prompt To Crew": "Explain why specialized agents improve clarity."
        },
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
