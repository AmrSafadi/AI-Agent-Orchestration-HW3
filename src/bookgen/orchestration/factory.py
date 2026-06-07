"""Shared dry-run/real construction scaffolding for agents and tasks.

Agent and task factories share the same shape: build kwargs, return a lightweight
dry-run dataclass by default, or the real CrewAI object when ``use_real_crewai``
is set. Centralizing it keeps ``agents.py`` and ``tasks.py`` small and DRY.

For real agents, the assigned CrewAI Skill objects (course Method 1) and the
configured model/temperature (``config/models.json``) are attached here so that
``agents.py`` stays focused on the role definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from bookgen.orchestration.skills import assigned_skill_names, load_skills

try:  # pragma: no cover - exercised only when CrewAI is installed locally.
    from crewai import Agent as CrewAIAgent
    from crewai import Task as CrewAITask
except ImportError:  # pragma: no cover - the fallback is covered via factories.
    CrewAIAgent = None
    CrewAITask = None


@dataclass
class DryRunAgent:
    """Minimal Agent-compatible object used when CrewAI is unavailable."""

    role: str
    goal: str
    backstory: str
    allow_delegation: bool = False
    verbose: bool = True
    skill_names: list[str] = field(default_factory=list)
    model: str | None = None


@dataclass
class DryRunTask:
    """Minimal Task-compatible object used when CrewAI is unavailable."""

    description: str
    expected_output: str
    agent: Any
    context: list[Any] = field(default_factory=list)


def crewai_available() -> bool:
    """Return whether the real CrewAI package is available."""
    return CrewAIAgent is not None and CrewAITask is not None


def _build_llm(model: str, temperature: float) -> Any:
    """Build a CrewAI LLM for the configured model (real runs only)."""
    from crewai import LLM  # local import: only needed on the real-crew path.

    return LLM(model=model, temperature=temperature)


def create_agent(
    role: str,
    goal: str,
    backstory: str,
    use_real_crewai: bool = False,
    agent_key: str | None = None,
    model: str | None = None,
    temperature: float = 0.0,
) -> Any:
    """Create a dry-run or real CrewAI Agent from the given fields."""
    skill_names = assigned_skill_names(agent_key) if agent_key else []
    agent_kwargs: dict[str, Any] = {
        "role": role,
        "goal": goal,
        "backstory": backstory,
        "allow_delegation": False,
        "verbose": True,
    }
    if not use_real_crewai:
        return DryRunAgent(skill_names=skill_names, model=model, **agent_kwargs)
    if CrewAIAgent is None:
        raise RuntimeError("CrewAI is not installed; real agent construction is unavailable.")
    skills = load_skills(agent_key) if agent_key else []
    if skills:
        agent_kwargs["skills"] = skills
    if model:
        agent_kwargs["llm"] = _build_llm(model, temperature)
    return CrewAIAgent(**agent_kwargs)


def create_task(
    description: str,
    expected_output: str,
    agent: Any,
    context: list[Any] | None = None,
    use_real_crewai: bool = False,
) -> Any:
    """Create a dry-run or real CrewAI Task from the given fields."""
    task_kwargs: dict[str, Any] = {
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
