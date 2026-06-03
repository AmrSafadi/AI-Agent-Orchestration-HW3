# FOLDER_STRUCTURE.md

## Why This Document Is Needed

This document defines where source code, documentation, configuration, generated artifacts, tests, templates, and final outputs should live.

It follows the course software guidelines, which explicitly emphasize a professional folder structure with `src/`, `tests/`, `docs/`, `config/`, `data/`, `results/` or generated outputs, `README.md`, `.env-example`, and `.gitignore`.

## Course-Specific Basis

| Course source | Structure consequence |
|---|---|
| `software_submission_guidelines-V3.pdf`, pp. 7-9 | Use README, docs, plan/TODO-style documentation, source package, tests, config, data, assets, results, `.env-example`, `.gitignore`. |
| Previous feedback report pp. 2-4 | Make planning, configuration, cost awareness, extensibility, and quality standards visible. |
| LangChain slides pp. 2-5, 14-15 | Separate harness concerns: config, context, tools/components, parsing, validation, outputs. |
| CrewAI Part B pp. 2-10 | Separate agents, tasks, crew assembly, and execution. |
| L06 p. 17 | Keep generated LaTeX, `.bib`, assets, and PDF outputs organized. |

## Detailed Draft

### Proposed Structure

```text
AI-Agent-Orchestration-HW3/
|
|-- README.md
|-- PROJECT_PLAN.md
|-- ARCHITECTURE.md
|-- AGENTS_DESIGN.md
|-- TASK_FLOW.md
|-- FOLDER_STRUCTURE.md
|-- pyproject.toml
|-- uv.lock
|-- .env.example
|-- .gitignore
|
|-- docs/
|   |-- PRD.md
|   |-- PLAN.md
|   |-- TODO.md
|   |-- ADRS.md
|   |-- COURSE_ALIGNMENT.md
|   |-- PROMPTS.md
|
|-- config/
|   |-- setup.json
|   |-- latex.json
|   |-- models.json
|   |-- budgets.json
|
|-- src/
|   |-- bookgen/
|       |-- __init__.py
|       |-- main.py
|       |
|       |-- orchestration/
|       |   |-- agents.py
|       |   |-- tasks.py
|       |   |-- crew.py
|       |   |-- process.py
|       |
|       |-- document/
|       |   |-- schemas.py
|       |   |-- artifacts.py
|       |   |-- validators.py
|       |
|       |-- harness/
|       |   |-- citations.py
|       |   |-- graph_generator.py
|       |   |-- assets.py
|       |   |-- evidence.py
|       |
|       |-- latex/
|       |   |-- renderer.py
|       |   |-- compiler.py
|       |   |-- escaping.py
|       |
|       |-- shared/
|           |-- config.py
|           |-- logging.py
|           |-- version.py
|
|-- templates/
|   |-- latex/
|       |-- main.tex.j2
|       |-- cover.tex.j2
|       |-- chapter.tex.j2
|       |-- table.tex.j2
|       |-- formula.tex.j2
|
|-- data/
|   |-- input/
|   |   |-- project_config.json
|   |   |-- source_registry.json
|   |
|   |-- intermediate/
|   |   |-- sample_book_plan.json
|   |   |-- sample_latex_spec.json
|   |   |-- sample_manuscript.md
|   |
|   |-- references/
|       |-- references.bib
|
|-- assets/
|   |-- images/
|   |-- static/
|
|-- generated/
|   |-- intermediate/
|   |   |-- book_plan.json
|   |   |-- research_pack.json
|   |   |-- manuscript.md
|   |   |-- review_report.json
|   |   |-- latex_spec.json
|   |
|   |-- latex/
|   |   |-- main.tex
|   |   |-- chapters/
|   |   |-- references.bib
|   |
|   |-- assets/
|   |   |-- graphs/
|   |   |-- images/
|   |
|   |-- reports/
|   |   |-- validation_report.json
|   |   |-- citation_report.json
|   |   |-- final_report.md
|   |
|   |-- pdf/
|       |-- final.pdf
|
|-- tests/
|   |-- unit/
|   |   |-- test_citations.py
|   |   |-- test_graph_generator.py
|   |   |-- test_validators.py
|   |   |-- test_latex_renderer.py
|   |
|   |-- integration/
|       |-- test_end_to_end_artifacts.py
|       |-- test_pdf_build_smoke.py
|
|-- scripts/
|   |-- build_pdf.py
|   |-- clean_generated.py
|   |-- validate_outputs.py
```

### Folder Responsibilities

#### Top-Level Planning Documents

The five requested planning documents live at the project root for easy grading:

- `PROJECT_PLAN.md`
- `ARCHITECTURE.md`
- `AGENTS_DESIGN.md`
- `TASK_FLOW.md`
- `FOLDER_STRUCTURE.md`

Reason:

- The user explicitly requested these documents.
- The previous feedback said a new reader should understand the vision and technical decisions before reading code.

#### `docs/`

Contains submission-style documentation:

- `PRD.md`: product requirements.
- `PLAN.md`: final architecture plan if the course expects this exact name.
- `TODO.md`: task tracking with status and definition of done.
- `ADRS.md`: architecture decision records.
- `COURSE_ALIGNMENT.md`: maps implementation evidence to lecture concepts.
- `PROMPTS.md`: final agent prompts/backstories/tasks for inspection.

Reason:

- The software guidelines call out mandatory documentation under `docs/`.

#### `config/`

Contains versioned configuration:

- model provider and model names,
- LaTeX engine,
- output paths,
- budget limits,
- build settings.

Secrets must stay in `.env`, never committed.

Reason:

- The previous feedback identified configuration portability and security as improvement areas.

#### `src/bookgen/orchestration/`

Contains CrewAI-specific definitions:

- agents,
- tasks,
- crew assembly,
- process selection.

Reason:

- Keeps CrewAI concepts visible and close to the lecture vocabulary.

#### `src/bookgen/document/`

Contains schemas, artifact loaders/savers, and validators.

Reason:

- Structured artifacts make task context explicit and easier to debug.

#### `src/bookgen/harness/`

Contains deterministic components:

- citation manager,
- graph generator,
- asset manager,
- evidence report generator.

Reason:

- The course harness concept separates model reasoning from reliable deterministic execution.

#### `src/bookgen/latex/`

Contains:

- renderer,
- compiler wrapper,
- escaping utilities.

Reason:

- LaTeX is a major assignment requirement and should not be hidden inside agent prompts.

#### `templates/latex/`

Contains reusable LaTeX templates.

Reason:

- Templates reduce compile failures and keep professional PDF structure consistent.

#### `data/intermediate/`

Contains committed example artifacts with the `sample_` prefix.

Reason:

- The grader can see representative artifact shapes without confusing examples with runtime outputs.

#### `generated/`

Contains files produced by runs:

- runtime intermediate artifacts,
- generated LaTeX,
- generated assets,
- validation/citation/build reports,
- final PDF.

Reason:

- Keeps outputs separate from source code and templates.

#### `tests/`

Tests deterministic components first:

- citation reconciliation,
- graph generation,
- validators,
- LaTeX rendering,
- PDF build smoke test.

Reason:

- Agents are probabilistic, but the harness must be testable. The software guidelines and previous feedback both reward testing and quality standards.

## Files Generated By Agents

| File | Agent |
|---|---|
| `generated/intermediate/book_plan.json` | Planner Agent |
| `generated/intermediate/research_pack.json` | Research Agent |
| `generated/intermediate/manuscript.md` or `.json` | Writer Agent |
| `generated/intermediate/review_report.json` | Reviewer Agent |
| `generated/intermediate/latex_spec.json` | LaTeX Agent |

## Files Generated By Deterministic Components

| File | Component |
|---|---|
| `data/references/references.bib` | CitationManager |
| `generated/assets/graphs/*.png` | GraphGenerator |
| `generated/reports/validation_report.json` | DocumentValidator |
| `generated/reports/citation_report.json` | CitationManager |
| `generated/latex/main.tex` | LatexRenderer |
| `generated/pdf/final.pdf` | PDFCompiler |

## Files Written By Developers

| Area | Files |
|---|---|
| Orchestration | CrewAI agent/task/crew definitions |
| Templates | LaTeX templates |
| Harness | citation, graph, validator, renderer, compiler |
| Config | setup/model/latex/budget config |
| Tests | unit and integration tests |
| Docs | README, PRD, plan, course alignment |

## Alternatives

| Alternative | Benefit | Risk |
|---|---|---|
| Put everything in one `main.py` | Fast initial demo. | Weak engineering structure and poor grading signal. |
| Store all outputs under `results/` | Matches some existing projects. | `generated/` more clearly separates generated files from analysis results. |
| Put planning docs only under `docs/` | Cleaner root. | User requested the five files by name; root-level is easier to find. |
| Skip templates and write TeX directly | Fewer files. | More fragile PDF compilation. |
| Skip tests for a homework | Saves time. | Contradicts software guidelines and previous feedback. |

## Risks

| Risk | Mitigation |
|---|---|
| Structure feels large before code exists. | Implement gradually; folders can start empty. |
| Generated files accidentally committed. | Use `.gitignore` for `generated/` except final evidence if required. |
| Existing repository files conflict with new package names. | Use a distinct package name such as `bookgen`. |
| Planning docs drift from implementation. | Update `docs/TODO.md` and ADRs during implementation. |
| Secrets leak through config. | Use `.env.example`, `.gitignore`, and no hardcoded API keys. |
