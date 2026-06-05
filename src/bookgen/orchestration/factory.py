"""Shared dry-run/real construction scaffolding for agents and tasks.

Agent and task factories share the same shape: build kwargs, return a lightweight
dry-run dataclass by default, or the real CrewAI object when ``use_real_crewai``
is set. Centralizing it keeps ``agents.py`` and ``tasks.py`` small and DRY.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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


def create_agent(
    role: str,
    goal: str,
    backstory: str,
    use_real_crewai: bool = False,
    skill_paths: list[str] | None = None,
) -> Any:
    """Create a dry-run or real CrewAI Agent from the given fields."""
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
