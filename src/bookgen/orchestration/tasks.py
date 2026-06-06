"""CrewAI task factory functions for the sequential document workflow.

The shared dry-run/real construction logic lives in ``orchestration.factory`` so
this module stays focused on the task descriptions and their context links.
"""

from __future__ import annotations

from typing import Any

from bookgen.orchestration.factory import create_task, crewai_available
from bookgen.orchestration.schema_contracts import (
    BOOK_PLAN_CONTRACT,
    LATEX_SPEC_CONTRACT,
    MANUSCRIPT_CONTRACT,
    RESEARCH_PACK_CONTRACT,
    REVIEW_REPORT_CONTRACT,
)

__all__ = [
    "create_planning_task",
    "create_research_task",
    "create_writing_task",
    "create_review_task",
    "create_latex_spec_task",
    "create_all_tasks",
    "crewai_available",
]


def create_planning_task(
    agent: Any, use_real_crewai: bool = False, topic: str = "the configured topic"
) -> Any:
    """Create the task that produces ``book_plan.json``."""
    return create_task(
        description=(
            f"Create the document plan for the topic: {topic}. Include title, subtitle, audience, "
            "chapter outline, section outline, required feature placement, estimated page count, "
            "and acceptance checklist."
        ),
        expected_output=(
            "A JSON object suitable for generated/intermediate/book_plan.json matching the BookPlan schema.\n"
            + BOOK_PLAN_CONTRACT
        ),
        agent=agent,
        use_real_crewai=use_real_crewai,
    )


def create_research_task(agent: Any, planning_task: Any, use_real_crewai: bool = False) -> Any:
    """Create the task that produces ``research_pack.json``."""
    return create_task(
        description=(
            "Use the book plan as context and create a research pack with key concepts, terminology, "
            "source candidates, notes per chapter, and unsupported-claim warnings."
        ),
        expected_output=(
            "A JSON object suitable for generated/intermediate/research_pack.json matching the ResearchPack schema.\n"
            + RESEARCH_PACK_CONTRACT
        ),
        agent=agent,
        context=[planning_task],
        use_real_crewai=use_real_crewai,
    )


def create_writing_task(
    agent: Any,
    planning_task: Any,
    research_task: Any,
    use_real_crewai: bool = False,
) -> Any:
    """Create the task that produces ``manuscript.md``."""
    return create_task(
        description=(
            "Use the book plan and research pack as context to draft the professional manuscript. "
            "Include citation markers and placeholders for image, graph, table, formula, and a "
            "Hebrew-English mixed section."
        ),
        expected_output=(
            "Markdown manuscript suitable for generated/intermediate/manuscript.md.\n"
            + MANUSCRIPT_CONTRACT
        ),
        agent=agent,
        context=[planning_task, research_task],
        use_real_crewai=use_real_crewai,
    )


def create_review_task(agent: Any, writing_task: Any, use_real_crewai: bool = False) -> Any:
    """Create the task that produces ``review_report.json``."""
    return create_task(
        description=(
            "Review the manuscript for clarity, consistency, assignment coverage, and course alignment. "
            "Report approval status, checklist results, notes, and required fixes."
        ),
        expected_output=(
            "A JSON object suitable for generated/intermediate/review_report.json matching the ReviewReport schema.\n"
            + REVIEW_REPORT_CONTRACT
        ),
        agent=agent,
        context=[writing_task],
        use_real_crewai=use_real_crewai,
    )


def create_latex_spec_task(agent: Any, review_task: Any, use_real_crewai: bool = False) -> Any:
    """Create the task that produces ``latex_spec.json``."""
    return create_task(
        description=(
            "Create the LaTeX assembly specification for the reviewed manuscript. Include template, "
            "chapter files, asset references, bibliography file, output PDF path, engine, and BiDi settings."
        ),
        expected_output=(
            "A JSON object suitable for generated/intermediate/latex_spec.json matching the LatexSpec schema.\n"
            + LATEX_SPEC_CONTRACT
        ),
        agent=agent,
        context=[review_task],
        use_real_crewai=use_real_crewai,
    )


def create_all_tasks(
    agents: dict[str, Any], use_real_crewai: bool = False, topic: str = "the configured topic"
) -> list[Any]:
    """Create all five sequential tasks with explicit context links."""
    planning_task = create_planning_task(
        agents["planner"], use_real_crewai=use_real_crewai, topic=topic
    )
    research_task = create_research_task(
        agents["research"], planning_task, use_real_crewai=use_real_crewai
    )
    writing_task = create_writing_task(
        agents["writer"], planning_task, research_task, use_real_crewai=use_real_crewai
    )
    review_task = create_review_task(
        agents["reviewer"], writing_task, use_real_crewai=use_real_crewai
    )
    latex_spec_task = create_latex_spec_task(
        agents["latex"], review_task, use_real_crewai=use_real_crewai
    )
    return [planning_task, research_task, writing_task, review_task, latex_spec_task]
