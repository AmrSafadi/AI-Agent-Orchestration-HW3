"""Deterministic LaTeX rendering from validated artifacts using Jinja2.

The Jinja environment uses ``\\VAR{}`` / ``\\BLOCK{}`` delimiters so it does not
clash with LaTeX's own braces. All agent-authored text is escaped first.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from bookgen.document.schemas import BookPlan, LatexSpec
from bookgen.latex.render_context import (
    DEFAULT_TEMPLATES_DIR,
    build_context,
    create_environment,
)

DEFAULT_OUTPUT_DIR = Path("generated/latex")


def render_main_tex(
    latex_spec: LatexSpec,
    book_plan: BookPlan,
    metadata: dict[str, str],
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    templates_dir: Path | str = DEFAULT_TEMPLATES_DIR,
    cite_key: str = "crewai_docs",
    references_bib: Path | str | None = None,
    root_dir: Path | str | None = None,
    manuscript_markdown: str | None = None,
) -> Path:
    """Render ``main.tex`` from the LaTeX spec and book plan; return its path."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    environment = create_environment(Path(templates_dir))
    asset_paths = _copy_assets_to_build(latex_spec, out_dir, Path(root_dir) if root_dir else None)
    context = build_context(
        latex_spec,
        book_plan,
        metadata,
        cite_key,
        asset_paths,
        manuscript_markdown=manuscript_markdown,
    )

    for template_name, filename in (
        ("table.tex.j2", context["table_file"]),
        ("formula.tex.j2", context["formula_file"]),
    ):
        if filename:
            snippet = environment.get_template(template_name).render(**context)
            (out_dir / filename).write_text(snippet, encoding="utf-8")

    main_tex = out_dir / "main.tex"
    main_tex.write_text(environment.get_template("main.tex.j2").render(**context), encoding="utf-8")

    if references_bib and Path(references_bib).exists():
        shutil.copyfile(references_bib, out_dir / Path(latex_spec.bibliography_file).name)
    return main_tex


def _copy_assets_to_build(
    latex_spec: LatexSpec,
    output_dir: Path,
    root_dir: Path | None,
) -> dict[str, str]:
    copied: dict[str, str] = {}
    for asset in latex_spec.assets:
        if asset.kind not in {"image", "graph"}:
            continue
        source = Path(asset.target_path)
        source = source if source.is_absolute() else (root_dir / source if root_dir else source)
        if not source.exists() or not source.is_file():
            continue
        target = output_dir / "assets" / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != target.resolve():
            shutil.copyfile(source, target)
        copied[asset.kind] = f"assets/{source.name}"
    return copied
