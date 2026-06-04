"""CrewAI agent factory functions.

The factories use CrewAI's public ``Agent`` class when CrewAI is installed.
For local dry-runs and tests, a small compatibility fallback is used so this
milestone never requires an API key or model provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - exercised only when CrewAI is installed locally.
    from crewai import Agent as CrewAIAgent
except ImportError:  # pragma: no cover - the fallback is covered via factories.
    CrewAIAgent = None

from bookgen.orchestration.skills import assigned_skill_paths


@dataclass
class DryRunAgent:
    """Minimal Agent-compatible object used when CrewAI is unavailable."""

    role: str
    goal: str
    backstory: str
    allow_delegation: bool = False
    verbose: bool = True


def create_planner_agent(use_real_crewai: bool = False) -> Any:
    """Create the Planner Agent."""
    return _create_agent(
        role="Document Planning Architect",
        goal=(
            "Create the book blueprint, including title, audience, chapter plan, "
            "section plan, required feature placement, page estimate, and acceptance checklist."
        ),
        backstory=(
            "You are a senior technical editor who turns broad assignment requirements "
            "into a clear, course-aligned document plan before any writing begins."
        ),
        use_real_crewai=use_real_crewai,
        skill_paths=assigned_skill_paths("planner"),
    )


def create_research_agent(use_real_crewai: bool = False) -> Any:
    """Create the Research Agent."""
    return _create_agent(
        role="Course-Aligned Research Analyst",
        goal=(
            "Create a focused research pack with key concepts, terminology, source candidates, "
            "chapter notes, and unsupported-claim warnings."
        ),
        backstory=(
            "You are a meticulous research analyst who connects every source and concept "
            "to the course vocabulary: Agent, Task, Crew, Process, context, harness, validation, "
            "observability, and LaTeX production."
        ),
        use_real_crewai=use_real_crewai,
        skill_paths=assigned_skill_paths("research"),
    )


def create_writer_agent(use_real_crewai: bool = False) -> Any:
    """Create the Writer Agent."""
    return _create_agent(
        role="Senior Technical Writer",
        goal=(
            "Write a professional manuscript from the plan and research context, including "
            "placeholders for citations, image, graph, table, formula, and Hebrew-English text."
        ),
        backstory=(
            "You transform structured research into clear prose. You work from context instead "
            "of inventing new sources, and you preserve the planned document structure."
        ),
        use_real_crewai=use_real_crewai,
        skill_paths=assigned_skill_paths("writer"),
    )


def create_reviewer_agent(use_real_crewai: bool = False) -> Any:
    """Create the Reviewer Agent."""
    return _create_agent(
        role="Senior Editorial Reviewer",
        goal=(
            "Review the manuscript for clarity, consistency, assignment coverage, and course alignment "
            "without changing the intended meaning."
        ),
        backstory=(
            "You are a careful senior reviewer who checks content quality and requirement coverage "
            "before deterministic validators inspect the technical artifacts."
        ),
        use_real_crewai=use_real_crewai,
        skill_paths=assigned_skill_paths("reviewer"),
    )


def create_latex_agent(use_real_crewai: bool = False) -> Any:
    """Create the LaTeX Agent."""
    return _create_agent(
        role="LaTeX Assembly Specialist",
        goal=(
            "Create a LaTeX assembly specification that maps the reviewed manuscript to templates, "
            "assets, bibliography, BiDi requirements, and output paths."
        ),
        backstory=(
            "You understand professional document structure and LaTeX production. You define "
            "assembly intent while deterministic Python components render and compile later."
        ),
        use_real_crewai=use_real_crewai,
        skill_paths=assigned_skill_paths("latex"),
    )


def create_all_agents(use_real_crewai: bool = False) -> dict[str, Any]:
    """Create all approved version-1 agents keyed by responsibility."""
    return {
        "planner": create_planner_agent(use_real_crewai=use_real_crewai),
        "research": create_research_agent(use_real_crewai=use_real_crewai),
        "writer": create_writer_agent(use_real_crewai=use_real_crewai),
        "reviewer": create_reviewer_agent(use_real_crewai=use_real_crewai),
        "latex": create_latex_agent(use_real_crewai=use_real_crewai),
    }


def crewai_available() -> bool:
    """Return whether the real CrewAI package is available."""
    return CrewAIAgent is not None


def _create_agent(
    role: str,
    goal: str,
    backstory: str,
    use_real_crewai: bool = False,
    skill_paths: list[str] | None = None,
) -> Any:
    agent_kwargs = {
        "role": role,
        "goal": goal,
        "backstory": backstory,
        "allow_delegation": False,
        "verbose": True,
    }
    if not use_real_crewai:
        return DryRunAgent(**agent_kwargs)
    if CrewAIAgent is None:
        raise RuntimeError("CrewAI is not installed; real agent construction is unavailable.")
    if skill_paths:
        agent_kwargs["skills"] = skill_paths
    return CrewAIAgent(**agent_kwargs)
