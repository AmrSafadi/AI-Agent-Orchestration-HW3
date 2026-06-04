"""Tests for CrewAI Skills discovery and per-agent assignment (no API)."""

from __future__ import annotations

from pathlib import Path

from bookgen.orchestration.skills import (
    SKILL_ASSIGNMENTS,
    SKILLS_ROOT,
    assigned_skill_paths,
    available_skill_names,
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


def test_every_assigned_skill_exists_on_disk() -> None:
    available = set(available_skill_names())
    for assigned in SKILL_ASSIGNMENTS.values():
        for name in assigned:
            assert name in available


def test_unknown_agent_has_no_skills() -> None:
    assert assigned_skill_paths("nonexistent") == []


def test_missing_skills_root_returns_empty(tmp_path: Path) -> None:
    assert available_skill_names(tmp_path / "nope") == []
