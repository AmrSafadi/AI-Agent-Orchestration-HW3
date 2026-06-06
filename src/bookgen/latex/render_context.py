"""Jinja context helpers for deterministic LaTeX rendering."""

from __future__ import annotations

from pathlib import Path

import jinja2

from bookgen.document.schemas import BookPlan, LatexSpec
from bookgen.latex.escaping import escape_latex

DEFAULT_TEMPLATES_DIR = Path("templates/latex")

# Cited per chapter (cycled) so every chapter carries an inline citation marker,
# not just the feature chapter. Keys must exist in the generated references.bib.
CHAPTER_CITE_KEYS = ("crewai_docs", "langchain_docs", "latex_project")


def create_environment(templates_dir: Path) -> jinja2.Environment:
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


def build_context(
    latex_spec: LatexSpec,
    book_plan: BookPlan,
    metadata: dict[str, str],
    cite_key: str,
    asset_paths: dict[str, str] | None = None,
) -> dict:
    """Build the Jinja render context from artifacts and run metadata."""
    image_path, image_caption = _asset(latex_spec, "image", asset_paths)
    graph_path, graph_caption = _asset(latex_spec, "graph", asset_paths)
    table_path, table_caption = _asset(latex_spec, "table")
    formula_path, _ = _asset(latex_spec, "formula")
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
        "table_file": Path(table_path).name,
        "formula_file": Path(formula_path).name,
        "chapters": _chapters(book_plan),
    }


def _asset(
    latex_spec: LatexSpec,
    kind: str,
    path_overrides: dict[str, str] | None = None,
) -> tuple[str, str]:
    for asset in latex_spec.assets:
        if asset.kind == kind:
            path = (
                path_overrides.get(kind, asset.target_path) if path_overrides else asset.target_path
            )
            return path, escape_latex(asset.caption or "")
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
