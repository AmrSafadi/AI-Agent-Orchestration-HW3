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
uv run --no-project --with pydantic python -m bookgen.main
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
PDF generation is not implemented yet.
```

## 3. Run Tests

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with pytest --with matplotlib python -m pytest tests/unit
```

Expected result:

```text
14 passed
```

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

## 5. What Not To Expect Yet

The current repository does not yet:

- call OpenAI or any LLM provider,
- generate final article content,
- render LaTeX,
- compile a PDF.

Those are future milestones.

