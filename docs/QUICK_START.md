# Quick Start

This guide shows how to run the current repository state.

## Prerequisites

- Python 3.10 or newer
- `uv`
- PowerShell on Windows

## 1. Open The Project

```powershell
cd <path-to>\AI-Agent-Orchestration-HW3
```

## 2. Run The Local Startup Check

This loads config, assembles the dry-run crew, and refreshes dry-run artifacts
from the committed `data/intermediate/sample_*` files. It does not call any API.

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main
```

Expected output:

```text
BookGen configuration loaded successfully.
Project title: AI Agent Orchestration HW3
Topic: Football Analytics and AI-Based Match Strategy
Output directory: ...\generated
Execution mode: DRY-RUN (default).
Crew assembled: 5 agents, 5 tasks, process=sequential.
Dry-run completed. CrewAI kickoff was not called.
Rendered LaTeX project: ...\generated\latex\main.tex
Rendered main.tex (LaTeX compilation not requested).
```

## 3. Run Tests

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with pytest --with pytest-cov --with matplotlib --with jinja2 python -m pytest tests --cov=bookgen
```

Expected result:

```text
145 passed, 2 skipped, 94.31% coverage
```

Coverage is 94.31% against an 85% gate, and ruff reports 0 violations.

## 4. Generate Deterministic Outputs

This creates the graph and bibliography only. It does not use CrewAI and does not compile a PDF.

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with matplotlib python -c "from bookgen.harness.graph_generator import generate_agent_pipeline_graph; from bookgen.harness.citations import generate_references_bib; generate_agent_pipeline_graph(); generate_references_bib()"
```

Outputs:

- `generated/assets/graphs/agent_pipeline_graph.png`
- `data/references/references.bib`

Dry-run CrewAI artifacts are written to `generated/intermediate/`:

- `book_plan.json`
- `research_pack.json`
- `manuscript.md`
- `review_report.json`
- `latex_spec.json`

The `data/intermediate/sample_*` files are committed examples for documentation, tests, and demos.

## 5. Render The LaTeX Project (And Optionally Build The PDF)

The dry-run already renders the full LaTeX project to `generated/latex/main.tex` from the
deterministic manuscript content. To also attempt a PDF compile, add `--build-pdf`:

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main --dry-run --build-pdf
```

The compiler runs lualatex -> biber -> lualatex -> lualatex and degrades gracefully when the
toolchain is absent. The document is primarily Hebrew (RTL), with English used only for
technical terms (Agent, Task, Crew, Harness, validation, ...); reproducing the final PDF requires
a free TeX toolchain (lualatex + biber) and the culmus David CLM Hebrew font.

## 6. Sample Output And Visual Evidence

The **final compiled PDF** is done: `--build-pdf` produces a 19-page, Hebrew-primary
`generated/pdf/final.pdf`, and a snapshot copy is committed at the repository root as `final.pdf`
so a grader sees it immediately on clone. It was verified by compiling locally with a TeX toolchain
(lualatex + biber) and the culmus "David CLM" Hebrew font: 19 pages covering the cover, table of
contents, an embedded image, a Python-generated graph, a table, a mathematical formula,
Hebrew-English BiDi text, and a bibliography with 3 resolved sources.

Screenshots of representative pages are committed under `assets/screenshots/`
for quick visual inspection: cover, chapter prose, feature page, table, and
bibliography.

Everything also works in the default dry-run, which never calls any LLM provider: the deterministic
football analytics manuscript content already exists and the dry-run renders
the complete LaTeX project to `generated/latex/main.tex`. The default `--dry-run` path does not
compile; reproducing the PDF from scratch requires a free TeX toolchain (lualatex + biber) plus the
culmus David CLM Hebrew font, after which `--build-pdf` compiles the project into the final PDF.

