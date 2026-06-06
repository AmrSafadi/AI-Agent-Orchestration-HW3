import pytest

import bookgen.orchestration.factory as factory
from bookgen.orchestration.agents import create_all_agents
from bookgen.orchestration.tasks import (
    create_all_tasks,
    create_latex_spec_task,
    create_planning_task,
    create_research_task,
    create_review_task,
    create_writing_task,
)


def test_tasks_can_be_constructed_with_expected_outputs() -> None:
    agents = create_all_agents()
    planning_task = create_planning_task(agents["planner"])
    research_task = create_research_task(agents["research"], planning_task)
    writing_task = create_writing_task(agents["writer"], planning_task, research_task)
    review_task = create_review_task(agents["reviewer"], writing_task)
    latex_task = create_latex_spec_task(agents["latex"], review_task)

    assert "book_plan.json" in planning_task.expected_output
    assert "research_pack.json" in research_task.expected_output
    assert "manuscript.md" in writing_task.expected_output
    assert "review_report.json" in review_task.expected_output
    assert "latex_spec.json" in latex_task.expected_output
    assert research_task.context == [planning_task]
    assert writing_task.context == [planning_task, research_task]
    assert review_task.context == [writing_task]
    assert latex_task.context == [review_task]
    assert '"chapters"' in planning_task.expected_output
    assert "chapterOutline" in planning_task.expected_output
    assert '"source_candidates"' in research_task.expected_output
    assert '"approved"' in review_task.expected_output
    assert '"main_template"' in latex_task.expected_output


def test_create_all_tasks_preserves_sequential_order() -> None:
    tasks = create_all_tasks(create_all_agents())

    assert len(tasks) == 5
    assert "book_plan.json" in tasks[0].expected_output
    assert "latex_spec.json" in tasks[-1].expected_output


def test_topic_is_injected_into_the_planning_task_description() -> None:
    tasks = create_all_tasks(create_all_agents(), topic="AI Agent Orchestration in Production")

    assert "AI Agent Orchestration in Production" in tasks[0].description


def test_create_all_tasks_rejects_missing_required_agent() -> None:
    agents = create_all_agents()
    agents.pop("latex")

    with pytest.raises(KeyError):
        create_all_tasks(agents)


def test_real_task_construction_requires_crewai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(factory, "CrewAITask", None)
    agents = create_all_agents()

    with pytest.raises(RuntimeError, match="CrewAI is not installed"):
        create_planning_task(agents["planner"], use_real_crewai=True)
