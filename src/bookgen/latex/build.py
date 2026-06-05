"""Wire the deterministic LaTeX pipeline: render, then optionally compile.

This is the end-to-end glue that makes the LaTeX layer invokable from the CLI.
Compilation degrades gracefully when no TeX toolchain is installed.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from bookgen.document.schemas import BookPlan, LatexSpec
from bookgen.harness.citations import generate_references_bib
from bookgen.latex.compiler import compile_pdf
from bookgen.latex.preflight import validate_rendered_citations
from bookgen.latex.renderer import DEFAULT_TEMPLATES_DIR, render_main_tex


def build_document(
    root_dir: Path | str = ".",
    metadata: dict[str, str] | None = None,
    compile_after: bool = False,
    latex_config: dict | None = None,
    templates_dir: Path | str = DEFAULT_TEMPLATES_DIR,
) -> dict:
    """Render ``main.tex`` from the generated artifacts and optionally compile it."""
    root = Path(root_dir)
    intermediate = root / "generated/intermediate"
    book_plan = BookPlan.model_validate_json(
        (intermediate / "book_plan.json").read_text(encoding="utf-8")
    )
    latex_spec = LatexSpec.model_validate_json(
        (intermediate / "latex_spec.json").read_text(encoding="utf-8")
    )

    references_bib = root / "data/references/references.bib"
    registry = root / "data/input/source_registry.json"
    if registry.exists() and not references_bib.exists():
        generate_references_bib(registry_path=registry, output_path=references_bib)
    main_tex = render_main_tex(
        latex_spec,
        book_plan,
        metadata or {},
        output_dir=root / "generated/latex",
        templates_dir=templates_dir,
        references_bib=references_bib if references_bib.exists() else None,
        root_dir=root,
    )

    summary: dict = {
        "main_tex": str(main_tex),
        "compiled": False,
        "message": "Rendered main.tex (LaTeX compilation not requested).",
        "features": _features_present(main_tex.read_text(encoding="utf-8")),
    }
    if compile_after:
        if registry.exists():
            citations = validate_rendered_citations(main_tex, registry)
            summary["citation_preflight"] = {
                "passed": citations.passed,
                "missing_keys": sorted(citations.missing_keys),
            }
            if not citations.passed:
                missing = ", ".join(sorted(citations.missing_keys))
                summary["message"] = f"Unresolved citation keys before compile: {missing}"
                return summary

        config = latex_config or {}
        result = compile_pdf(
            main_tex,
            engine=config.get("engine", "lualatex"),
            bib_backend=config.get("bibliography_backend", "biber"),
            passes=config.get("passes", 4),
            fallback_engine=config.get("fallback_engine"),
        )
        summary["compiled"] = result.success
        summary["message"] = result.message
        summary["pdf"] = str(result.pdf_path) if result.pdf_path else None
        summary["pages"] = result.pages
        summary["warnings"] = result.warnings
        if result.success and result.pdf_path:
            final_pdf = root / config.get("output_pdf", "generated/pdf/final.pdf")
            final_pdf.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(result.pdf_path, final_pdf)
            summary["final_pdf"] = str(final_pdf)
    return summary


# Markers expected in the rendered main.tex for each required assignment feature.
_FEATURE_MARKERS = {
    "cover": "\\begin{titlepage}",
    "toc": "\\tableofcontents",
    "image_or_graph": "\\includegraphics",
    "table_or_formula": "\\input{",
    "bidi": "\\begin{english}",
    "bibliography": "\\printbibliography",
    "citation": "\\cite{",
}


def _features_present(tex_text: str) -> list[str]:
    """Return which required document features are present in the rendered LaTeX."""
    return [name for name, marker in _FEATURE_MARKERS.items() if marker in tex_text]
