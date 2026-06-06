"""Tests for the deterministic LaTeX renderer."""

from __future__ import annotations

from bookgen.latex.renderer import render_main_tex


def test_render_main_tex_contains_required_features(
    tmp_path, render_latex_spec, render_book_plan, render_meta
) -> None:
    out = render_main_tex(
        render_latex_spec, render_book_plan(), metadata=render_meta, output_dir=tmp_path
    )
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
    # LaTeX spec's declared asset paths exist. Chapter bodies are inlined directly
    # into main.tex (no orphaned per-chapter files).
    assert "\\begin{tabular}" in (out.parent / "t.tex").read_text(encoding="utf-8")
    assert "\\begin{equation}" in (out.parent / "f.tex").read_text(encoding="utf-8")
    assert not (out.parent / "chapters").exists()


def test_render_escapes_special_characters(
    tmp_path, render_latex_spec, render_book_plan, render_meta
) -> None:
    out = render_main_tex(
        render_latex_spec,
        render_book_plan(purpose="50% & up"),
        metadata=render_meta,
        output_dir=tmp_path,
    )
    assert "50\\% \\& up" in out.read_text(encoding="utf-8")


def test_render_copies_bibliography(
    tmp_path, render_latex_spec, render_book_plan, render_meta
) -> None:
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    bib = source_dir / "references.bib"
    bib.write_text("@online{crewai_docs, title={x}}\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    render_main_tex(
        render_latex_spec,
        render_book_plan(),
        metadata=render_meta,
        output_dir=out_dir,
        references_bib=bib,
    )
    assert (out_dir / "references.bib").exists()


def test_render_copies_image_and_graph_assets_into_build_dir(
    tmp_path, render_latex_spec, render_book_plan, render_meta
) -> None:
    root = tmp_path / "root"
    (root / "assets").mkdir(parents=True)
    (root / "assets/img.png").write_bytes(b"image")
    (root / "assets/g.png").write_bytes(b"graph")
    out_dir = root / "generated/latex"

    out = render_main_tex(
        render_latex_spec,
        render_book_plan(),
        metadata=render_meta,
        output_dir=out_dir,
        root_dir=root,
    )

    assert (out_dir / "assets/img.png").read_bytes() == b"image"
    assert (out_dir / "assets/g.png").read_bytes() == b"graph"
    assert "\\includegraphics[width=0.6\\textwidth]{assets/img.png}" in out.read_text(
        encoding="utf-8"
    )
