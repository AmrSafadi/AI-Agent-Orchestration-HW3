"""CrewAI Skills: discover knowledge packs and assign them to agents.

A Skill is a knowledge pack (a ``SKILL.md`` with YAML frontmatter + Markdown
instructions) injected into an agent — the course's CrewAI Skill concept. Unlike
a Tool (an action capability), a Skill provides know-how via prompt injection.
Skills live under the repo-level ``skills/`` directory; CrewAI loads them through
the ``skills=`` parameter when a real crew runs.
"""

from __future__ import annotations

from pathlib import Path

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


def assigned_skill_paths(agent_key: str, skills_root: Path | str = SKILLS_ROOT) -> list[str]:
    """Return existing skill-directory paths assigned to an agent (as strings)."""
    root = Path(skills_root)
    paths: list[str] = []
    for name in SKILL_ASSIGNMENTS.get(agent_key, ()):
        skill_dir = root / name
        if (skill_dir / "SKILL.md").is_file():
            paths.append(str(skill_dir))
    return paths
