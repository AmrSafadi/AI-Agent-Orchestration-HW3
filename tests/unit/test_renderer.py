"""Tests for the deterministic LaTeX renderer."""

from __future__ import annotations

from pathlib import Path

from bookgen.document.schemas import (
    BookPlan,
    LatexAsset,
    LatexSpec,
    PlannedChapter,
    PlannedSection,
)
from bookgen.latex.renderer import render_main_tex

META = {
    "author": "Sharbel",
    "course": "AI Agent Orchestration",
    "lecturer": "Dr. Segal",
    "date": "2026",
}


def _book_plan(purpose: str = "Explain the basics.") -> BookPlan:
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


def _latex_spec() -> LatexSpec:
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


def test_render_main_tex_contains_required_features(tmp_path: Path) -> None:
    out = render_main_tex(_latex_spec(), _book_plan(), metadata=META, output_dir=tmp_path)
    tex = out.read_text(encoding="utf-8")
    for needle in (
        "\\tableofcontents",
        "\\includegraphics",
        "\\begin{tabular}",
        "\\begin{equation}",
        "\\begin{hebrew}",
        "\\printbibliography",
        "\\cite{crewai_docs}",
        "\\chapter{Foundations}",
    ):
        assert needle in tex, needle


def test_render_escapes_special_characters(tmp_path: Path) -> None:
    out = render_main_tex(
        _latex_spec(), _book_plan(purpose="50% & up"), metadata=META, output_dir=tmp_path
    )
    assert "50\\% \\& up" in out.read_text(encoding="utf-8")


def test_render_copies_bibliography(tmp_path: Path) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    bib = source_dir / "references.bib"
    bib.write_text("@online{crewai_docs, title={x}}\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    render_main_tex(
        _latex_spec(), _book_plan(), metadata=META, output_dir=out_dir, references_bib=bib
    )
    assert (out_dir / "references.bib").exists()
