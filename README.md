# AI Agent Orchestration HW3

CrewAI-based article/book generator with deterministic LaTeX PDF production.

This repository is being built for a university course on AI Agent Orchestration. The final system will use a small sequential CrewAI crew to generate a professional article/book and then use deterministic Python components to produce a reliable LaTeX project and final PDF.

## Naming Note

The `HW3` name is intentional. The previous `HW2` project folder contains the Exercise 02 debate assignment. This repository is for the course's Article/Book Generation with CrewAI and LaTeX assignment, treated here as Homework/Assignment 3.

## Current Status

Completed:

- Planning documents
- Project skeleton
- Configuration loading
- Pydantic artifact schemas
- Deterministic graph generation
- Deterministic citation registry and BibTeX generation
- Deterministic document requirement validation
- CrewAI agent, task, and crew definitions
- Dry-run crew execution path that creates/reuses intermediate artifacts without API calls
- Sample data and unit tests
- Repository documentation milestone

Not implemented yet:

- LLM/API calls
- LaTeX rendering
- PDF compilation

## Start Here

| Need | Document |
|---|---|
| Full project vision | [docs/PROJECT_BLUEPRINT.md](docs/PROJECT_BLUEPRINT.md) |
| Course concept mapping | [docs/COURSE_ALIGNMENT.md](docs/COURSE_ALIGNMENT.md) |
| Architecture diagrams | [docs/ARCHITECTURE_DIAGRAM.md](docs/ARCHITECTURE_DIAGRAM.md) |
| Current progress | [docs/IMPLEMENTATION_STATUS.md](docs/IMPLEMENTATION_STATUS.md) |
| Setup and commands | [docs/QUICK_START.md](docs/QUICK_START.md) |
| Contribution rules | [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) |

The blueprint is the single source of truth for the intended final system.

## Planned Workflow

1. Load project configuration from `config/`.
2. Run a sequential CrewAI workflow with five agents:
   - Planner Agent
   - Research Agent
   - Writer Agent
   - Reviewer Agent
   - LaTeX Agent
3. Save structured intermediate artifacts.
4. Use deterministic Python components for citation management, graph generation, validation, LaTeX rendering, and PDF compilation.
5. Produce a final professional PDF with cover page, table of contents, chapters, citations, images, a Python graph, formula, table, and Hebrew-English mixed text.

## Quick Commands

Run the local startup check:

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic python -m bookgen.main --dry-run
```

Run tests:

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with pytest --with matplotlib python -m pytest tests/unit
```

Generate deterministic harness outputs:

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with matplotlib python -c "from bookgen.harness.graph_generator import generate_agent_pipeline_graph; from bookgen.harness.citations import generate_references_bib; generate_agent_pipeline_graph(); generate_references_bib()"
```

Run real CrewAI execution only when explicitly approved and configured:

```powershell
$env:OPENAI_API_KEY="..."
$env:PYTHONPATH="src"
uv run python -m bookgen.main --run-crew
```

## Important Boundary

The default implementation path is intentionally local and deterministic. It does not call OpenAI and does not compile a PDF. Real CrewAI execution requires the explicit `--run-crew` flag and `OPENAI_API_KEY`.
