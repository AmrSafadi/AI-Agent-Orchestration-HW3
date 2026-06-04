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

This loads config, assembles the dry-run crew, and creates or reuses dry-run artifacts. It does not call any API.

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main
```

Expected output:

```text
BookGen configuration loaded successfully.
Project title: AI Agent Orchestration HW3
Topic: AI Agent Orchestration: From Prompting to Production-Ready Crews
Output directory: ...\generated
Artifact output directory: ...\generated\intermediate
Execution mode: DRY-RUN (default). CrewAI kickoff will not be called.
Crew assembled: 5 agents, 5 tasks, process=sequential.
Dry-run completed. CrewAI kickoff was not called.
Rendered LaTeX project: ...\generated\latex\main.tex
LaTeX render status: OK (PDF compile skipped; run with --build-pdf when a TeX toolchain is installed).
```

## 3. Run Tests

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with pytest --with matplotlib --with jinja2 python -m pytest tests
```

Expected result:

```text
77 passed
```

Coverage is 93.41% against an 85% gate, and ruff reports 0 violations.

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
technical terms (Agent, Task, Crew, Harness, validation, ...); rendering the final PDF requires
a free TeX toolchain (lualatex + biber) and the David CLM Hebrew font.

## 6. What Not To Expect Yet

The only step still blocked is producing the **final compiled PDF**, and it is blocked solely on
installing a free TeX toolchain (lualatex + biber) plus the David CLM Hebrew font, neither of which
is present locally. It is not blocked on missing code.

Everything else already works in the default dry-run, which never calls any LLM provider: the
deterministic manuscript content already exists (~3,260 Hebrew words across 6 chapters) and the
dry-run renders the complete LaTeX project to `generated/latex/main.tex`. Once the toolchain and
font are installed, `--build-pdf` compiles that project into the final PDF.

