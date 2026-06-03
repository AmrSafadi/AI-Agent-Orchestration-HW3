# Implementation Status

This document tracks what is complete, what is in progress, and what remains.

## Completed Milestones

| Milestone | Status | Evidence |
|---|---|---|
| 0. Planning | Complete | Root planning documents: `PROJECT_PLAN.md`, `ARCHITECTURE.md`, `AGENTS_DESIGN.md`, `TASK_FLOW.md`, `FOLDER_STRUCTURE.md`. |
| 1. Skeleton | Complete | `README.md`, `pyproject.toml`, config files, package folders, placeholder modules. |
| 2. Config and Schemas | Complete | `src/bookgen/shared/config.py`, `src/bookgen/shared/logging.py`, `src/bookgen/document/schemas.py`, tests. |
| 3. Deterministic Harness | Complete | `graph_generator.py`, `citations.py`, `validators.py`, sample data, generated graph, generated bibliography, tests. |
| Documentation | Complete | `docs/PROJECT_BLUEPRINT.md`, `COURSE_ALIGNMENT.md`, `IMPLEMENTATION_STATUS.md`, `ARCHITECTURE_DIAGRAM.md`, `QUICK_START.md`, `CONTRIBUTING.md`. |
| 4. CrewAI Definitions | Complete | `agents.py`, `tasks.py`, `crew.py`, CLI dry-run mode, orchestration tests. |

## In Progress

No implementation milestone is currently in progress.

The next implementation milestone should be Milestone 5: sequential crew execution with controlled artifact persistence.

## Future Milestones

| Milestone | Goal | Notes |
|---|---|---|
| 5. Sequential Crew Execution | Add controlled non-dry-run execution and artifact persistence. | Must remain opt-in and API-key guarded. |
| 6. Artifact Generation | Persist real intermediate outputs from task results. | Write runtime artifacts to `generated/intermediate/`; keep `sample_` files as committed examples. |
| 7. LaTeX Rendering | Render `.tex` files from templates. | Still no PDF compilation unless requested. |
| 8. PDF Compilation | Compile final PDF with LuaLaTeX/XeLaTeX and bibliography backend. | Capture build logs and validation report. |
| 9. Submission Polish | README evidence, tests, final cleanup. | Prepare course-grader walkthrough. |

## Current Test Command

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with pytest --with matplotlib python -m pytest tests/unit
```

Known passing result from Milestone 4:

```text
14 passed
```

## Current Generated Outputs

| Output | Path |
|---|---|
| Agent pipeline graph | `generated/assets/graphs/agent_pipeline_graph.png` |
| Dry-run BookPlan | `generated/intermediate/book_plan.json` |
| Dry-run ResearchPack | `generated/intermediate/research_pack.json` |
| Dry-run manuscript | `generated/intermediate/manuscript.md` |
| Dry-run review report | `generated/intermediate/review_report.json` |
| Dry-run LaTeX spec | `generated/intermediate/latex_spec.json` |
| Bibliography | `data/references/references.bib` |

## Not Yet Implemented

- LLM provider integration
- API key usage
- LaTeX renderer
- PDF compiler
- final PDF

## Status Rules

When future milestones are completed:

1. Update this file.
2. Update `docs/PROJECT_BLUEPRINT.md` if the project vision changes.
3. Add or update tests.
4. Keep README short and point to docs.

