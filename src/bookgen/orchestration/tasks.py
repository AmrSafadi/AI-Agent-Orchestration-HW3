"""CrewAI task factory functions for the sequential document workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:  # pragma: no cover - exercised only when CrewAI is installed locally.
    from crewai import Task as CrewAITask
except ImportError:  # pragma: no cover - the fallback is covered via factories.
    CrewAITask = None


@dataclass
class DryRunTask:
    """Minimal Task-compatible object used when CrewAI is unavailable."""

    description: str
    expected_output: str
    agent: Any
    context: list[Any] = field(default_factory=list)


def create_planning_task(
    agent: Any, use_real_crewai: bool = False, topic: str = "the configured topic"
) -> Any:
    """Create the task that produces ``book_plan.json``."""
    return _create_task(
        description=(
            f"Create the document plan for the topic: {topic}. Include title, subtitle, audience, "
            "chapter outline, section outline, required feature placement, estimated page count, "
            "and acceptance checklist."
        ),
        expected_output=(
            "A JSON object suitable for generated/intermediate/book_plan.json matching the BookPlan schema."
        ),
        agent=agent,
        use_real_crewai=use_real_crewai,
    )


def create_research_task(agent: Any, planning_task: Any, use_real_crewai: bool = False) -> Any:
    """Create the task that produces ``research_pack.json``."""
    return _create_task(
        description=(
            "Use the book plan as context and create a research pack with key concepts, terminology, "
            "source candidates, notes per chapter, and unsupported-claim warnings."
        ),
        expected_output=(
            "A JSON object suitable for generated/intermediate/research_pack.json matching the ResearchPack schema."
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
    return _create_task(
        description=(
            "Use the book plan and research pack as context to draft the professional manuscript. "
            "Include citation markers and placeholders for image, graph, table, formula, and a "
            "Hebrew-English mixed section."
        ),
        expected_output="Markdown manuscript suitable for generated/intermediate/manuscript.md.",
        agent=agent,
        context=[planning_task, research_task],
        use_real_crewai=use_real_crewai,
    )


def create_review_task(agent: Any, writing_task: Any, use_real_crewai: bool = False) -> Any:
    """Create the task that produces ``review_report.json``."""
    return _create_task(
        description=(
            "Review the manuscript for clarity, consistency, assignment coverage, and course alignment. "
            "Report approval status, checklist results, notes, and required fixes."
        ),
        expected_output=(
            "A JSON object suitable for generated/intermediate/review_report.json matching the ReviewReport schema."
        ),
        agent=agent,
        context=[writing_task],
        use_real_crewai=use_real_crewai,
    )


def create_latex_spec_task(agent: Any, review_task: Any, use_real_crewai: bool = False) -> Any:
    """Create the task that produces ``latex_spec.json``."""
    return _create_task(
        description=(
            "Create the LaTeX assembly specification for the reviewed manuscript. Include template, "
            "chapter files, asset references, bibliography file, output PDF path, engine, and BiDi settings."
        ),
        expected_output=(
            "A JSON object suitable for generated/intermediate/latex_spec.json matching the LatexSpec schema."
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
        agents["research"],
        planning_task,
        use_real_crewai=use_real_crewai,
    )
    writing_task = create_writing_task(
        agents["writer"],
        planning_task,
        research_task,
        use_real_crewai=use_real_crewai,
    )
    review_task = create_review_task(
        agents["reviewer"],
        writing_task,
        use_real_crewai=use_real_crewai,
    )
    latex_spec_task = create_latex_spec_task(
        agents["latex"],
        review_task,
        use_real_crewai=use_real_crewai,
    )
    return [planning_task, research_task, writing_task, review_task, latex_spec_task]


def crewai_available() -> bool:
    """Return whether the real CrewAI package is available."""
    return CrewAITask is not None


def _create_task(
    description: str,
    expected_output: str,
    agent: Any,
    context: list[Any] | None = None,
    use_real_crewai: bool = False,
) -> Any:
    task_kwargs = {
        "description": description,
        "expected_output": expected_output,
        "agent": agent,
    }
    if context:
        task_kwargs["context"] = context

    if not use_real_crewai:
        return DryRunTask(
            context=context or [],
            **{key: task_kwargs[key] for key in task_kwargs if key != "context"},
        )
    if CrewAITask is None:
        raise RuntimeError("CrewAI is not installed; real task construction is unavailable.")
    return CrewAITask(**task_kwargs)
