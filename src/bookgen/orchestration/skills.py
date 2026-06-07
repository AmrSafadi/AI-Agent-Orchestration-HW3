"""CrewAI Skills: discover knowledge packs and assign them to agents.

A Skill is a knowledge pack (a ``SKILL.md`` with YAML frontmatter + Markdown
instructions) injected into an agent — the course's CrewAI Skill concept. Unlike
a Tool (an action capability), a Skill provides know-how via prompt injection.
Skills live under the repo-level ``skills/`` directory.

Per-agent assignment (course Method 1) attaches the assigned, *activated*
``Skill`` objects to each real agent. We pass ``Skill`` objects (not directory
paths) because CrewAI's ``Agent.set_skills`` only resolves filesystem entries via
``discover_skills`` on the *parent* skills directory or via pre-loaded ``Skill``
objects — a leaf-directory string is silently ignored. ``load_skills`` therefore
discovers under the parent root and returns activated objects ready for
``Agent(skills=...)``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

SKILLS_ROOT = Path(__file__).resolve().parents[3] / "skills"

# Course Method 1: each approved agent receives specific skills.
SKILL_ASSIGNMENTS: dict[str, tuple[str, ...]] = {
    "planner": ("course-alignment",),
    "research": ("citation-discipline", "course-alignment"),
    "writer": ("latex-style", "course-alignment"),
    "reviewer": ("course-alignment",),
    "latex": ("latex-style",),
}


def available_skill_names(skills_root: Path | str = SKILLS_ROOT) -> list[str]:
    """Return the names of skill directories that contain a ``SKILL.md`` file."""
    root = Path(skills_root)
    if not root.exists():
        return []
    return sorted(
        child.name for child in root.iterdir() if child.is_dir() and (child / "SKILL.md").is_file()
    )


def assigned_skill_names(agent_key: str, skills_root: Path | str = SKILLS_ROOT) -> list[str]:
    """Return the skill names assigned to an agent that actually exist on disk."""
    available = set(available_skill_names(skills_root))
    return [name for name in SKILL_ASSIGNMENTS.get(agent_key, ()) if name in available]


def assigned_skill_paths(agent_key: str, skills_root: Path | str = SKILLS_ROOT) -> list[str]:
    """Return existing skill-directory paths assigned to an agent (as strings)."""
    root = Path(skills_root)
    return [str(root / name) for name in assigned_skill_names(agent_key, skills_root)]


def load_skills(agent_key: str, skills_root: Path | str = SKILLS_ROOT) -> list[Any]:
    """Discover and activate the CrewAI ``Skill`` objects assigned to an agent.

    Returns activated ``Skill`` objects ready to pass to ``Agent(skills=...)``.
    Returns an empty list when no skills are assigned or CrewAI is unavailable.
    """
    names = set(assigned_skill_names(agent_key, skills_root))
    if not names:
        return []
    try:
        from crewai.skills import activate_skill, discover_skills
    except ImportError:  # pragma: no cover - CrewAI is a project dependency.
        return []
    discovered = [skill for skill in discover_skills(Path(skills_root)) if skill.name in names]
    return [activate_skill(skill) for skill in discovered]
