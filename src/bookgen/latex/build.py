"""Wire the deterministic LaTeX pipeline: render, then optionally compile.

This is the end-to-end glue that makes the LaTeX layer invokable from the CLI.
Compilation degrades gracefully when no TeX toolchain is installed.
"""

from __future__ import annotations

from pathlib import Path

from bookgen.document.schemas import BookPlan, LatexSpec
from bookgen.harness.citations import generate_references_bib
from bookgen.latex.compiler import compile_pdf
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
    )

    summary: dict = {
        "main_tex": str(main_tex),
        "compiled": False,
        "message": "Rendered main.tex (LaTeX compilation not requested).",
    }
    if compile_after:
        config = latex_config or {}
        result = compile_pdf(
            main_tex,
            engine=config.get("engine", "lualatex"),
            bib_backend=config.get("bibliography_backend", "biber"),
            passes=config.get("passes", 4),
        )
        summary["compiled"] = result.success
        summary["message"] = result.message
        summary["pdf"] = str(result.pdf_path) if result.pdf_path else None
    return summary
