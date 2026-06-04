# Usage & Interface (UI/UX)

Required by the documentation and UI/UX standards. The system is a command-line
tool (no GUI); this document lets a reader understand the experience **without
running it**.

## 1. Interface type

A single CLI entry point, `bookgen.main`, run via `uv`. There is no graphical
interface; all interaction is through flags and printed status output.

## 2. Commands & modes

Set `$env:PYTHONPATH="src"` first (PowerShell).

| Goal | Command | Calls API? |
|---|---|---|
| Startup check (default) | `uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main` | No |
| Explicit dry-run | `… python -m bookgen.main --dry-run` | No |
| Real crew run | `… python -m bookgen.main --run-crew` (needs `OPENAI_API_KEY`) | Yes |
| Run tests | `uv run --no-project --with pydantic --with pytest --with matplotlib --with jinja2 python -m pytest tests/unit` | No |

`--dry-run` and `--run-crew` are mutually exclusive; dry-run is the default.

## 3. What the user sees (sample dry-run session)

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

## 4. UX qualities (Nielsen heuristics)

- **Visibility of system status:** prints loaded config, execution mode, crew
  composition, and an explicit completion line.
- **Error prevention / safe defaults:** dry-run is the default; the real path
  needs both `--run-crew` and `OPENAI_API_KEY`, and fails with a clear
  `RuntimeError` if the key is missing.
- **Match to the real world:** vocabulary mirrors the course (agents, tasks,
  crew, process, dry-run).
- **User control & freedom:** explicit, mutually exclusive mode flags.

## 5. Outputs the user can inspect

After a run: artifacts under `generated/intermediate/` (`book_plan`,
`research_pack`, `manuscript`, `review_report`, `latex_spec`); the pipeline graph
under `generated/assets/graphs/`; the bibliography at
`data/references/references.bib`. Committed `data/intermediate/sample_*` files
show representative shapes without running anything.

## 6. Planned

Screenshots of representative runs and a fuller Nielsen-heuristics review are
tracked in TODO. When the LaTeX pipeline lands, the final PDF becomes the primary
visual deliverable.
