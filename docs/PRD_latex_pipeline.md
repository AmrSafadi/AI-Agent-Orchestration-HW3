# Specialized PRD — LaTeX Rendering & PDF Compilation

Dedicated PRD per submission guideline 2.3 for a central mechanism. Parent
requirements: [PRD.md](PRD.md). Design context: [PLAN.md](PLAN.md),
`TASK_FLOW.md`.

## 1. Mechanism Description and Background

The LaTeX pipeline converts validated, structured artifacts into a professional
PDF. It has two deterministic stages:

1. **Renderer** (`latex/renderer.py`): consumes `latex_spec.json`, the structured
   `book_plan.json` (BookPlan) from which it renders all chapter/section text,
   generated assets, and `references.bib`, then renders `main.tex` and chapter
   `.tex` files from Jinja2 templates in `templates/latex/`. It owns LaTeX
   escaping (`latex/escaping.py`) so agent text cannot break the build.
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
- `book_plan.json` (BookPlan schema): the structured source of all chapter and
  section text the renderer typesets (the renderer does not read a
  `manuscript.md`).
- `data/references/references.bib` (from the citation mechanism); when absent it
  is generated from `data/input/source_registry.json` by `latex/build.py`.
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
chapter, and a resolved bibliography. The document is primarily Hebrew (RTL):
`templates/latex/main.tex.j2` sets `\setmainlanguage{hebrew}` with
`\setmainfont{David CLM}`, English is used LTR only for technical terms, and an
explicit `\begin{english}` block in `chapter.tex.j2` demonstrates the RTL→LTR
BiDi transition. `config/latex.json` `language_support` is now
`primary="hebrew"`, `secondary="english"`.

The assignment features (embedded image, Python-generated graph, typeset table,
formula, and the English LTR BiDi block) render on the **first chapter** via
`show_features` (`renderer.py` sets `index == 0`; gated by
`\BLOCK{if chapter.show_features}` in `chapter.tex.j2`), so feature tests target
the first chapter. Every chapter additionally emits an inline `\cite`.

**Test scenarios.**
- *Renderer unit tests* (`tests/unit/test_renderer.py`): given a sample
  `latex_spec.json` and `book_plan.json`, assert the rendered first-chapter
  `.tex` includes `\tableofcontents`, `\includegraphics`, a `tabular`, an
  equation environment, a `\begin{english}` BiDi block, and an inline `\cite`;
  assert special characters are escaped.
- *End-to-end artifacts test* (`tests/integration/test_end_to_end_artifacts.py`):
  drive the deterministic pipeline and assert the rendered `.tex` artifacts are
  produced. A dedicated PDF compile smoke test is planned (not yet implemented)
  and would be skipped when no toolchain is on PATH.
- *Manual acceptance check*: verify page count, clickable citations, rendered
  math/table, and BiDi correctness in the produced PDF.
