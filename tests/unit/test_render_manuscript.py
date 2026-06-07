"""Tests for manuscript-driven rendering (strong Markdown -> main.tex)."""

from __future__ import annotations

from bookgen.latex.renderer import render_main_tex


def _quality_manuscript(point: str = "Strong manuscript point") -> str:
    hebrew_word = "סוכן"
    chapters = []
    for index in range(1, 6):
        body = " ".join([hebrew_word] * 330)
        chapters.append(
            f"## Manuscript Chapter {index}\n\n"
            f"### Manuscript Section {index}\n\n"
            f"{point} {index}. {body} [@crewai_docs]."
        )
    return "# AI Agent Orchestration\n\n" + "\n\n".join(chapters)


def test_render_uses_quality_manuscript_when_available(
    tmp_path, render_latex_spec, render_book_plan, render_meta
) -> None:
    out = render_main_tex(
        render_latex_spec,
        render_book_plan(purpose="Fallback plan prose."),
        metadata=render_meta,
        output_dir=tmp_path,
        manuscript_markdown=_quality_manuscript(),
    )

    main_tex = out.read_text(encoding="utf-8")
    assert "Strong manuscript point" in main_tex
    assert "\\cite{crewai_docs}" in main_tex
    assert "Fallback plan prose" not in main_tex


def test_render_falls_back_when_manuscript_is_shallow(
    tmp_path, render_latex_spec, render_book_plan, render_meta
) -> None:
    out = render_main_tex(
        render_latex_spec,
        render_book_plan(purpose="Fallback plan prose."),
        metadata=render_meta,
        output_dir=tmp_path,
        manuscript_markdown="# Draft\n\n## One\n\nPlaceholder.",
    )

    main_tex = out.read_text(encoding="utf-8")
    assert "Fallback plan prose" in main_tex
    assert "Placeholder" not in main_tex
