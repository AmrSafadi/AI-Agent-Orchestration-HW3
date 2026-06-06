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
        "\\input{t.tex}",
        "\\input{f.tex}",
        "\\setmainlanguage{hebrew}",
        "\\begin{english}",
        "\\printbibliography",
        "\\cite{crewai_docs}",
        "\\chapter{Foundations}",
    ):
        assert needle in tex, needle

    # The table and formula are materialized as standalone files on disk so the
    # LaTeX spec's declared asset paths exist (validate_latex_spec_files).
    assert "\\begin{tabular}" in (out.parent / "t.tex").read_text(encoding="utf-8")
    assert "\\begin{equation}" in (out.parent / "f.tex").read_text(encoding="utf-8")
    assert (out.parent / "chapters/chapter_01.tex").exists()


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


def test_render_copies_image_and_graph_assets_into_build_dir(tmp_path: Path) -> None:
    root = tmp_path / "root"
    (root / "assets").mkdir(parents=True)
    (root / "assets/img.png").write_bytes(b"image")
    (root / "assets/g.png").write_bytes(b"graph")
    out_dir = root / "generated/latex"

    out = render_main_tex(
        _latex_spec(),
        _book_plan(),
        metadata=META,
        output_dir=out_dir,
        root_dir=root,
    )

    assert (out_dir / "assets/img.png").read_bytes() == b"image"
    assert (out_dir / "assets/g.png").read_bytes() == b"graph"
    assert "\\includegraphics[width=0.6\\textwidth]{assets/img.png}" in out.read_text(
        encoding="utf-8"
    )


def test_render_uses_quality_manuscript_when_available(tmp_path: Path) -> None:
    out = render_main_tex(
        _latex_spec(),
        _book_plan(purpose="Fallback plan prose."),
        metadata=META,
        output_dir=tmp_path,
        manuscript_markdown=_quality_manuscript(),
    )

    chapter = (out.parent / "chapters/chapter_01.tex").read_text(encoding="utf-8")
    assert "Strong manuscript point" in chapter
    assert "\\cite{crewai_docs}" in chapter
    assert "Fallback plan prose" not in chapter


def test_render_falls_back_when_manuscript_is_shallow(tmp_path: Path) -> None:
    out = render_main_tex(
        _latex_spec(),
        _book_plan(purpose="Fallback plan prose."),
        metadata=META,
        output_dir=tmp_path,
        manuscript_markdown="# Draft\n\n## One\n\nPlaceholder.",
    )

    chapter = (out.parent / "chapters/chapter_01.tex").read_text(encoding="utf-8")
    assert "Fallback plan prose" in chapter
    assert "Placeholder" not in chapter


def _quality_manuscript() -> str:
    hebrew_word = "\u05e1\u05d5\u05db\u05df"
    chapters = []
    for index in range(1, 6):
        body = " ".join([hebrew_word] * 330)
        chapters.append(
            f"## Manuscript Chapter {index}\n\n"
            f"### Manuscript Section {index}\n\n"
            f"Strong manuscript point {index}. {body} [@crewai_docs]."
        )
    return "# AI Agent Orchestration\n\n" + "\n\n".join(chapters)
