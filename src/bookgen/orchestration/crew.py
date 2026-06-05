"""CrewAI crew assembly with dry-run safety as the default behavior."""

from __future__ import annotations

import os
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
from bookgen.orchestration.dry_run import EXPECTED_ARTIFACTS, create_or_reuse_dry_run_artifacts
from bookgen.orchestration.tasks import create_all_tasks
from bookgen.shared.config import load_config, project_root
from bookgen.shared.gatekeeper import ApiGatekeeper

__all__ = [
    "EXPECTED_ARTIFACTS",
    "CrewRunResult",
    "DryRunCrew",
    "build_crew",
    "create_document_generation_crew",
    "create_or_reuse_dry_run_artifacts",
    "run_crew",
]


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


def build_crew(use_real_crewai: bool = False, topic: str = "the configured topic") -> Any:
    """Create the sequential CrewAI crew, or a dry-run-compatible crew object."""
    agents_by_name = create_all_agents(use_real_crewai=use_real_crewai)
    tasks = create_all_tasks(agents_by_name, use_real_crewai=use_real_crewai, topic=topic)
    agents = list(agents_by_name.values())

    if not use_real_crewai:
        return DryRunCrew(agents=agents, tasks=tasks)
    if CrewAICrew is None or CrewAIProcess is None:
        raise RuntimeError("CrewAI is not installed; real crew execution is unavailable.")

    return CrewAICrew(agents=agents, tasks=tasks, process=CrewAIProcess.sequential, verbose=True)


def create_document_generation_crew(use_real_crewai: bool = False) -> Any:
    """Backward-compatible alias for ``build_crew``."""
    return build_crew(use_real_crewai=use_real_crewai)


def run_crew(dry_run: bool = True, root_dir: Path | str | None = None) -> CrewRunResult:
    """Run the crew safely.

    Dry-run is the default and never calls ``kickoff``. It refreshes the
    expected runtime artifacts from committed samples so later deterministic
    milestones can be tested without an API key or stale generated state.
    """
    root = Path(root_dir) if root_dir else project_root()

    if dry_run:
        crew = build_crew(use_real_crewai=False)
        print(_describe_crew(crew))
        artifacts = create_or_reuse_dry_run_artifacts(root)
        message = "Dry-run completed. CrewAI kickoff was not called."
        print(message)
        return CrewRunResult(dry_run=True, message=message, artifacts=artifacts)

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for real CrewAI execution.")

    app_config = load_config(root / "config")
    topic = app_config.setup.project.topic
    crew = build_crew(use_real_crewai=True, topic=topic)
    print(_describe_crew(crew))

    gatekeeper = ApiGatekeeper(app_config.rate_limits)
    try:
        result = gatekeeper.execute(crew.kickoff, inputs={"topic": topic})
    except Exception as exc:
        raise RuntimeError(f"Real CrewAI execution failed: {exc}") from exc
    message = "Real CrewAI execution completed."
    print(message)
    return CrewRunResult(dry_run=False, message=message, artifacts=[], output=result)


def _describe_crew(crew: Any) -> str:
    process = getattr(crew, "process", "sequential")
    return (
        "Crew assembled: "
        f"{len(getattr(crew, 'agents', []))} agents, "
        f"{len(getattr(crew, 'tasks', []))} tasks, "
        f"process={process}."
    )
