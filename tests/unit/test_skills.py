"""Tests for CrewAI Skills discovery and per-agent assignment (no API key)."""

from __future__ import annotations

from pathlib import Path

import pytest

from bookgen.orchestration.agents import create_writer_agent
from bookgen.orchestration.factory import crewai_available
from bookgen.orchestration.skills import (
    SKILL_ASSIGNMENTS,
    SKILLS_ROOT,
    assigned_skill_names,
    assigned_skill_paths,
    available_skill_names,
    load_skills,
)

EXPECTED_SKILLS = {"latex-style", "citation-discipline", "course-alignment"}


def test_available_skill_names_lists_all_packs() -> None:
    assert EXPECTED_SKILLS.issubset(set(available_skill_names()))


def test_each_skill_has_frontmatter() -> None:
    for name in EXPECTED_SKILLS:
        text = (SKILLS_ROOT / name / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---")
        assert "name:" in text
        assert "description:" in text


def test_writer_is_assigned_latex_and_alignment() -> None:
    paths = assigned_skill_paths("writer")
    assert any(path.endswith("latex-style") for path in paths)
    assert any(path.endswith("course-alignment") for path in paths)


def test_assigned_skill_names_filter_to_existing() -> None:
    names = assigned_skill_names("writer")
    assert {"latex-style", "course-alignment"} <= set(names)
    assert assigned_skill_names("nonexistent") == []


def test_every_assigned_skill_exists_on_disk() -> None:
    available = set(available_skill_names())
    for assigned in SKILL_ASSIGNMENTS.values():
        for name in assigned:
            assert name in available


def test_unknown_agent_has_no_skills() -> None:
    assert assigned_skill_paths("nonexistent") == []


def test_missing_skills_root_returns_empty(tmp_path: Path) -> None:
    assert available_skill_names(tmp_path / "nope") == []


def test_dry_run_agent_exposes_assigned_skill_names() -> None:
    agent = create_writer_agent()
    assert "latex-style" in agent.skill_names
    assert "course-alignment" in agent.skill_names


def test_load_skills_returns_activated_objects() -> None:
    if not crewai_available():
        pytest.skip("CrewAI not installed")
    skills = load_skills("writer")
    assert {skill.name for skill in skills} >= {"latex-style", "course-alignment"}


def test_real_agent_has_skills_attached() -> None:
    """Regression: leaf-dir string paths were silently dropped; objects must attach."""
    if not crewai_available():
        pytest.skip("CrewAI not installed")
    agent = create_writer_agent(use_real_crewai=True)
    assert agent.skills, "writer skills must attach to a real CrewAI agent"
    assert {skill.name for skill in agent.skills} >= {"latex-style", "course-alignment"}
