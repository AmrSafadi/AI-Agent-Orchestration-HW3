# Specialized PRD — LaTeX Rendering & PDF Compilation

Dedicated PRD per submission guideline 2.3 for a central mechanism. Parent
requirements: [PRD.md](PRD.md). Design context: [PLAN.md](PLAN.md),
`TASK_FLOW.md`.

## 1. Mechanism Description and Background

The LaTeX pipeline converts validated, structured artifacts into a professional
PDF. It has two deterministic stages:

1. **Renderer** (`latex/renderer.py`): consumes `latex_spec.json`, the reviewed
   manuscript, generated assets, and `references.bib`, then renders `main.tex`
   and chapter `.tex` files from Jinja2 templates in `templates/latex/`. It owns
   LaTeX escaping (`latex/escaping.py`) so agent text cannot break the build.
2. **Compiler** (`latex/compiler.py`): runs the LaTeX toolchain to produce
   `final.pdf`, capturing `build.log`.

**Theoretical background.** Citations and cross-references require multiple
compilation passes: the first pass emits `.aux`/`.bcf` data, the bibliography
backend (biber) resolves references, and subsequent passes incorporate them.
The canonical sequence is:

```text
lualatex -> biber -> lualatex -> lualatex
```

Hebrew–English bidirectional text requires a Unicode-aware engine (LuaLaTeX or
XeLaTeX) with explicit language/BiDi handling (e.g., polyglossia + bidi), which
pdfLaTeX cannot provide reliably.

## 2. Inputs / Outputs

**Inputs**
- `generated/intermediate/latex_spec.json` (LatexSpec schema): template choice,
  chapter mapping, asset references, BiDi metadata, engine, output path.
- Reviewed manuscript (`manuscript.md`).
- `data/references/references.bib` (from the citation mechanism).
- Generated assets (graph PNG, image, table data, formula metadata).
- LaTeX config (`config/latex.json`): engine, fallback, bib backend.

**Outputs**
- Rendered `generated/latex/main.tex` and `chapters/*.tex`.
- `generated/pdf/final.pdf`.
- `generated/reports/build.log` and an updated `validation_report.json`.

## 3. Requirements and Performance Metrics

- Render must escape all unsafe characters and never emit invalid LaTeX from
  arbitrary agent text.
- Compile must succeed for the standard document and produce ≥ 15 pages.
- Multi-pass build must resolve all citations and cross-references (no `??`).
- BiDi chapter must show correct LTR/RTL transitions.
- Engine: LuaLaTeX default, XeLaTeX fallback; biber for the bibliography.
- Graceful degradation: a missing toolchain yields a clear error and preserved
  `.tex` output, not a crash.

## 4. Constraints and Limitations

- Requires an installed TeX distribution (MiKTeX/TeX Live) with LuaLaTeX + biber;
  the renderer stage works without it, the compiler stage does not.
- The LaTeX agent specifies intent only; it must never invoke a compiler
  (ADR-5). All fragile syntax is owned by Python.
- File-size rule: split rendering helpers to keep each file ≤ 150 code lines.

## 5. Alternatives Considered

| Alternative | Why not chosen |
|---|---|
| pdfLaTeX | Weak Unicode/BiDi support for Hebrew. |
| Agent writes `.tex` directly | Fragile, unescaped, non-reproducible. |
| Single-pass compile | Citations/cross-refs would not resolve. |
| Pandoc Markdown→PDF | Less control over professional structure and BiDi. |

## 6. Success Criteria and Test Scenarios

**Success criteria.** A reproducible `final.pdf` with cover, TOC, ≥ 15 pages,
embedded image and Python graph, a typeset table and formula, a correct BiDi
chapter, and a resolved bibliography.

**Test scenarios.**
- *Renderer unit tests* (`tests/unit/test_latex_renderer.py`): given a sample
  `latex_spec.json`, assert the rendered `.tex` includes `\tableofcontents`,
  `\includegraphics`, a `tabular`, an equation environment, and a BiDi block;
  assert special characters are escaped.
- *Compile smoke test* (`tests/integration/test_pdf_build_smoke.py`): compile a
  minimal document and assert a non-empty PDF and a clean `build.log`
  (skipped if no toolchain is on PATH).
- *Manual acceptance check*: verify page count, clickable citations, rendered
  math/table, and BiDi correctness in the produced PDF.
