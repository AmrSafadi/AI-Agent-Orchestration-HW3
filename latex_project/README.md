# LaTeX Project

This folder contains the LaTeX project sources for the submitted PDF:

- `main.tex` - rendered LaTeX document.
- `references.bib` - bibliography used by biber.
- `agent_roles_table.tex` - table snippet included by `main.tex`.
- `quality_score_formula.tex` - formula snippet included by `main.tex`.
- `assets/` - image and Python-generated graph PNGs.
- `chapters/` - rendered chapter source files kept for inspection.

The repository root `final.pdf` is the verified submission snapshot. To rebuild
from the project root, use:

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main --dry-run --build-pdf
```

Manual LaTeX compilation requires LuaLaTeX, biber, and the Hebrew `David CLM`
font from the culmus package.
