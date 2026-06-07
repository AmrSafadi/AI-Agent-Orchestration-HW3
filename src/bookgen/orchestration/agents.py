"""CrewAI agent factory functions.

Each factory builds one of the approved version-1 agents. The shared dry-run/real
construction logic (Skill attachment + model selection) lives in
``orchestration.factory``; the role/goal/backstory definitions live in ``_SPECS``
so the five public factories stay thin and DRY.
"""

from __future__ import annotations

from typing import Any

from bookgen.orchestration.factory import create_agent, crewai_available

__all__ = [
    "create_planner_agent",
    "create_research_agent",
    "create_writer_agent",
    "create_reviewer_agent",
    "create_latex_agent",
    "create_all_agents",
    "crewai_available",
]

# (role, goal, backstory) for each approved agent key, in pipeline order.
_SPECS: dict[str, tuple[str, str, str]] = {
    "planner": (
        "Document Planning Architect",
        "Create the book blueprint, including title, audience, chapter plan, section plan, "
        "required feature placement, page estimate, and acceptance checklist.",
        "You are a senior technical editor who turns broad assignment requirements into a "
        "clear, course-aligned document plan before any writing begins.",
    ),
    "research": (
        "Course-Aligned Research Analyst",
        "Create a focused research pack with key concepts, terminology, source candidates, "
        "chapter notes, and unsupported-claim warnings.",
        "You are a meticulous research analyst who connects every source and concept to the "
        "course vocabulary: Agent, Task, Crew, Process, context, harness, validation, LaTeX.",
    ),
    "writer": (
        "Senior Technical Writer",
        "Write a professional manuscript from the plan and research context, including "
        "placeholders for citations, image, graph, table, formula, and Hebrew-English text.",
        "You transform structured research into clear prose. You work from context instead of "
        "inventing new sources, and you preserve the planned document structure.",
    ),
    "reviewer": (
        "Senior Editorial Reviewer",
        "Review the manuscript for clarity, consistency, assignment coverage, and course "
        "alignment without changing the intended meaning.",
        "You are a careful senior reviewer who checks content quality and requirement coverage "
        "before deterministic validators inspect the technical artifacts.",
    ),
    "latex": (
        "LaTeX Assembly Specialist",
        "Create a LaTeX assembly specification that maps the reviewed manuscript to templates, "
        "assets, bibliography, BiDi requirements, and output paths.",
        "You understand professional document structure and LaTeX production. You define "
        "assembly intent while deterministic Python components render and compile later.",
    ),
}


def _make(key: str, use_real_crewai: bool, model: str | None, temperature: float) -> Any:
    """Build one approved agent from its ``_SPECS`` entry."""
    role, goal, backstory = _SPECS[key]
    return create_agent(
        role=role,
        goal=goal,
        backstory=backstory,
        use_real_crewai=use_real_crewai,
        agent_key=key,
        model=model,
        temperature=temperature,
    )


def create_planner_agent(
    use_real_crewai: bool = False, model: str | None = None, temperature: float = 0.0
) -> Any:
    """Create the Planner Agent."""
    return _make("planner", use_real_crewai, model, temperature)


def create_research_agent(
    use_real_crewai: bool = False, model: str | None = None, temperature: float = 0.0
) -> Any:
    """Create the Research Agent."""
    return _make("research", use_real_crewai, model, temperature)


def create_writer_agent(
    use_real_crewai: bool = False, model: str | None = None, temperature: float = 0.0
) -> Any:
    """Create the Writer Agent."""
    return _make("writer", use_real_crewai, model, temperature)


def create_reviewer_agent(
    use_real_crewai: bool = False, model: str | None = None, temperature: float = 0.0
) -> Any:
    """Create the Reviewer Agent."""
    return _make("reviewer", use_real_crewai, model, temperature)


def create_latex_agent(
    use_real_crewai: bool = False, model: str | None = None, temperature: float = 0.0
) -> Any:
    """Create the LaTeX Agent."""
    return _make("latex", use_real_crewai, model, temperature)


def create_all_agents(use_real_crewai: bool = False, models: Any | None = None) -> dict[str, Any]:
    """Create all approved version-1 agents keyed by responsibility.

    When ``models`` (a ``ModelsConfig``) is supplied, each agent is built with its
    configured model/temperature so ``config/models.json`` drives real runs.
    """
    temperature = float(models.temperature) if models else 0.0

    def model_for(role: str) -> str | None:
        """Resolve the configured model for a role (None in dry-run)."""
        if models is None:
            return None
        return models.agent_models.get(role, models.default_model)

    return {key: _make(key, use_real_crewai, model_for(key), temperature) for key in _SPECS}
