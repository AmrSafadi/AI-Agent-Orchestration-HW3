"""Sanity test for the committed authored book content."""

from __future__ import annotations

from pathlib import Path

from bookgen.document.schemas import BookPlan

SAMPLE = Path("data/intermediate/sample_book_plan.json")


def test_sample_book_plan_is_valid_and_substantial() -> None:
    plan = BookPlan.model_validate_json(SAMPLE.read_text(encoding="utf-8"))
    assert len(plan.chapters) >= 6
    words = sum(
        len(section.purpose.split()) for chapter in plan.chapters for section in chapter.sections
    )
    assert words >= 3000, f"authored content too short ({words} words) for a ~15-page document"
