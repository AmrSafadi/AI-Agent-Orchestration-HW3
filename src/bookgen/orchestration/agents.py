"""CrewAI agent factory functions.

Each factory builds one of the approved version-1 agents. The shared dry-run/real
construction logic lives in ``orchestration.factory`` so this module stays focused
on the agent roles themselves.
"""

from __future__ import annotations

from typing import Any

from bookgen.orchestration.factory import create_agent, crewai_available
from bookgen.orchestration.skills import assigned_skill_paths

__all__ = [
    "create_planner_agent",
    "create_research_agent",
    "create_writer_agent",
    "create_reviewer_agent",
    "create_latex_agent",
    "create_all_agents",
    "crewai_available",
]


def create_planner_agent(use_real_crewai: bool = False) -> Any:
    """Create the Planner Agent."""
    return create_agent(
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
    return create_agent(
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
    return create_agent(
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
    return create_agent(
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
    return create_agent(
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
