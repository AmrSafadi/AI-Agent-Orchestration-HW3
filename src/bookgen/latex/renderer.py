"""Deterministic LaTeX rendering from validated artifacts using Jinja2.

The Jinja environment uses ``\\VAR{}`` / ``\\BLOCK{}`` delimiters so it does not
clash with LaTeX's own braces. All agent-authored text is escaped first.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import jinja2

from bookgen.document.schemas import BookPlan, LatexSpec
from bookgen.latex.escaping import escape_latex

DEFAULT_TEMPLATES_DIR = Path("templates/latex")
DEFAULT_OUTPUT_DIR = Path("generated/latex")

# Cited per chapter (cycled) so every chapter carries an inline citation marker,
# not just the feature chapter. Keys must exist in the generated references.bib.
CHAPTER_CITE_KEYS = ("crewai_docs", "langchain_docs", "latex_project")


def _environment(templates_dir: Path) -> jinja2.Environment:
    """Return a Jinja2 environment using LaTeX-safe delimiters."""
    return jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        loader=jinja2.FileSystemLoader(str(templates_dir)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _asset(latex_spec: LatexSpec, kind: str) -> tuple[str, str]:
    for asset in latex_spec.assets:
        if asset.kind == kind:
            return asset.target_path, escape_latex(asset.caption or "")
    return "", ""


def _chapters(book_plan: BookPlan) -> list[dict]:
    rendered = []
    for index, chapter in enumerate(book_plan.chapters):
        rendered.append(
            {
                "title": escape_latex(chapter.title),
                "sections": [
                    {"title": escape_latex(section.title), "content": escape_latex(section.purpose)}
                    for section in chapter.sections
                ],
                "show_features": index == 0,
                "cite_key": CHAPTER_CITE_KEYS[index % len(CHAPTER_CITE_KEYS)],
            }
        )
    return rendered


def build_context(
    latex_spec: LatexSpec,
    book_plan: BookPlan,
    metadata: dict[str, str],
    cite_key: str,
) -> dict:
    """Build the Jinja render context from the artifacts and run metadata."""
    image_path, image_caption = _asset(latex_spec, "image")
    graph_path, graph_caption = _asset(latex_spec, "graph")
    _, table_caption = _asset(latex_spec, "table")
    return {
        "title": escape_latex(latex_spec.title or book_plan.title),
        "subtitle": escape_latex(book_plan.subtitle or ""),
        "author": escape_latex(metadata.get("author", "")),
        "course": escape_latex(metadata.get("course", "")),
        "lecturer": escape_latex(metadata.get("lecturer", "")),
        "date": escape_latex(metadata.get("date", "")),
        "bib_resource": Path(latex_spec.bibliography_file).stem,
        "cite_key": cite_key,
        "image_path": image_path,
        "image_caption": image_caption,
        "graph_path": graph_path,
        "graph_caption": graph_caption,
        "table_caption": table_caption,
        "chapters": _chapters(book_plan),
    }


def render_main_tex(
    latex_spec: LatexSpec,
    book_plan: BookPlan,
    metadata: dict[str, str],
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    templates_dir: Path | str = DEFAULT_TEMPLATES_DIR,
    cite_key: str = "crewai_docs",
    references_bib: Path | str | None = None,
) -> Path:
    """Render ``main.tex`` from the LaTeX spec and book plan; return its path."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    template = _environment(Path(templates_dir)).get_template("main.tex.j2")
    context = build_context(latex_spec, book_plan, metadata, cite_key)
    main_tex = out_dir / "main.tex"
    main_tex.write_text(template.render(**context), encoding="utf-8")

    if references_bib and Path(references_bib).exists():
        shutil.copyfile(references_bib, out_dir / Path(latex_spec.bibliography_file).name)
    return main_tex
