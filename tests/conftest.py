"""Shared pytest fixtures for document-validation tests."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from bookgen.document.schemas import (
    BookPlan,
    LatexAsset,
    LatexSpec,
    PlannedChapter,
    PlannedSection,
)

_DEFAULT_MANUSCRIPT = (
    "Introduction citing CrewAI [@crewai_docs]. "
    "מערכת סוכנים חכמה combined with English technical terms."
)


@pytest.fixture
def default_book_plan() -> dict:
    """A complete BookPlan dict that satisfies every feature check."""
    return {
        "title": "AI Agent Orchestration",
        "audience": "Course evaluator",
        "chapters": [
            {
                "title": "Foundations",
                "summary": "A short chapter.",
                "sections": [{"title": "CrewAI", "purpose": "Explain the basics."}],
            }
        ],
        "required_feature_placement": {"cover": "front matter", "toc": "front matter"},
        "acceptance_checklist": ["cover", "toc"],
        "estimated_pages": 15,
    }


@pytest.fixture
def default_latex_spec() -> dict:
    """A LatexSpec dict listing all four required asset kinds."""
    return {
        "title": "AI Agent Orchestration",
        "engine": "lualatex",
        "main_template": "main.tex.j2",
        "output_pdf": "generated/pdf/final.pdf",
        "chapter_files": ["chapters/chapter_01.tex"],
        "assets": [
            {"asset_id": "img1", "kind": "image", "target_path": "assets/img.png"},
            {"asset_id": "g1", "kind": "graph", "target_path": "assets/graph.png"},
            {"asset_id": "t1", "kind": "table", "target_path": "tables/t.tex"},
            {"asset_id": "f1", "kind": "formula", "target_path": "formulas/f.tex"},
        ],
        "bibliography_file": "data/references/references.bib",
        "bidi_required": True,
    }


@pytest.fixture
def default_manuscript() -> str:
    """Manuscript text with a citation marker plus Hebrew and Latin script."""
    return _DEFAULT_MANUSCRIPT


@pytest.fixture
def render_meta() -> dict:
    """Document metadata used by the renderer tests."""
    return {
        "author": "Sharbel",
        "course": "AI Agent Orchestration",
        "lecturer": "Dr. Segal",
        "date": "2026",
    }


@pytest.fixture
def render_book_plan() -> Callable[..., BookPlan]:
    """Return a factory building a single-chapter BookPlan for renderer tests."""

    def _make(purpose: str = "Explain the basics.") -> BookPlan:
        return BookPlan(
            title="AI Agents",
            subtitle="From Prompting to Production",
            audience="Evaluator",
            chapters=[
                PlannedChapter(
                    title="Foundations",
                    summary="s",
                    sections=[PlannedSection(title="CrewAI", purpose=purpose)],
                )
            ],
            acceptance_checklist=["cover"],
            estimated_pages=15,
        )

    return _make


@pytest.fixture
def render_latex_spec() -> LatexSpec:
    """A LatexSpec listing all four required asset kinds for renderer tests."""
    return LatexSpec(
        title="AI Agents",
        engine="lualatex",
        main_template="main.tex.j2",
        output_pdf="generated/pdf/final.pdf",
        chapter_files=["chapters/chapter_01.tex"],
        assets=[
            LatexAsset(asset_id="img", kind="image", target_path="assets/img.png", caption="Img"),
            LatexAsset(asset_id="g", kind="graph", target_path="assets/g.png", caption="Graph"),
            LatexAsset(asset_id="t", kind="table", target_path="t.tex", caption="Roles"),
            LatexAsset(asset_id="f", kind="formula", target_path="f.tex", caption="Q"),
        ],
        bibliography_file="data/references/references.bib",
    )


@pytest.fixture
def write_features(
    tmp_path: Path,
) -> Callable[[dict, dict, str], tuple[Path, Path, Path]]:
    """Return a factory that writes plan/spec/manuscript files and returns their paths."""

    def _write(book_plan: dict, latex_spec: dict, manuscript: str) -> tuple[Path, Path, Path]:
        book_plan_path = tmp_path / "book_plan.json"
        latex_spec_path = tmp_path / "latex_spec.json"
        manuscript_path = tmp_path / "manuscript.md"
        book_plan_path.write_text(json.dumps(book_plan), encoding="utf-8")
        latex_spec_path.write_text(json.dumps(latex_spec), encoding="utf-8")
        manuscript_path.write_text(manuscript, encoding="utf-8")
        return book_plan_path, latex_spec_path, manuscript_path

    return _write
