import pytest
from pydantic import ValidationError

from bookgen.document.schemas import BookPlan, PlannedChapter, PlannedSection


def test_create_valid_book_plan() -> None:
    plan = BookPlan(
        title="AI Agent Orchestration",
        subtitle="From Prompting to Production",
        audience="University course evaluator",
        chapters=[
            PlannedChapter(
                title="CrewAI Foundations",
                summary="Introduces Agent, Task, Crew, and Process.",
                sections=[
                    PlannedSection(
                        title="Agent Teams",
                        purpose="Explain why multiple roles are useful.",
                    )
                ],
            )
        ],
        required_feature_placement={"graph": "Chapter 2"},
        acceptance_checklist=["cover page", "table of contents"],
        estimated_pages=15,
    )

    assert plan.title == "AI Agent Orchestration"
    assert plan.chapters[0].sections[0].title == "Agent Teams"


def test_invalid_book_plan_rejects_missing_chapters() -> None:
    with pytest.raises(ValidationError):
        BookPlan(
            title="AI Agent Orchestration",
            audience="University course evaluator",
            chapters=[],
            acceptance_checklist=["cover page"],
            estimated_pages=15,
        )
