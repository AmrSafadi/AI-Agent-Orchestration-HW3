import pytest

import bookgen.orchestration.factory as factory
from bookgen.orchestration.agents import (
    create_all_agents,
    create_latex_agent,
    create_planner_agent,
    create_research_agent,
    create_reviewer_agent,
    create_writer_agent,
)


def test_agents_can_be_constructed() -> None:
    agents = [
        create_planner_agent(),
        create_research_agent(),
        create_writer_agent(),
        create_reviewer_agent(),
        create_latex_agent(),
    ]

    assert [agent.role for agent in agents] == [
        "Document Planning Architect",
        "Course-Aligned Research Analyst",
        "Senior Technical Writer",
        "Senior Editorial Reviewer",
        "LaTeX Assembly Specialist",
    ]
    assert all(agent.allow_delegation is False for agent in agents)
    assert all(agent.verbose is True for agent in agents)


def test_create_all_agents_uses_approved_agent_names() -> None:
    agents = create_all_agents()

    assert list(agents) == ["planner", "research", "writer", "reviewer", "latex"]


def test_real_agent_construction_requires_crewai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(factory, "CrewAIAgent", None)

    with pytest.raises(RuntimeError, match="CrewAI is not installed"):
        create_planner_agent(use_real_crewai=True)
