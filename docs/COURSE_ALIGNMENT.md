# Course Alignment

This document maps course concepts to concrete project components.

| Course concept | Meaning in course context | Project component |
|---|---|---|
| Agent | A specialized worker with role, goal, backstory, and possible tools. | `src/bookgen/orchestration/agents.py` defines Planner, Research, Writer, Reviewer, and LaTeX agent factories. |
| Task | A measurable work unit with description and expected output. | `src/bookgen/orchestration/tasks.py` defines plan, research, writing, review, and LaTeX-spec task factories. |
| Crew | The team that combines agents and tasks. | `src/bookgen/orchestration/crew.py` assembles the five-agent crew with dry-run safety. |
| Process | The execution strategy for the crew. | Version 1 uses `Process.sequential`, configured through `config/setup.json`. |
| Context | Output from one task passed to later tasks. | The dry-run pipeline already passes and persists structured artifacts under `generated/intermediate/` (`book_plan.json`, `research_pack.json`, `manuscript.md`, `review_report.json`, `latex_spec.json`) via `src/bookgen/orchestration/dry_run.py` and `crew.py`. |
| Harness | The software system around the model. | `src/bookgen/shared`, `src/bookgen/document`, `src/bookgen/harness`, `src/bookgen/latex`, `src/bookgen/sdk` (BookGenSDK facade), and `src/bookgen/research` (`sensitivity.py`). |
| Tools/Skills | Reliable capabilities that support agents. | Deterministic CitationManager (`src/bookgen/harness/citations.py`), GraphGenerator (`src/bookgen/harness/graph_generator.py`), Validator (`src/bookgen/document/validators.py`), and the implemented LaTeX Renderer and PDFCompiler (`src/bookgen/latex/renderer.py`, `compiler.py`, `escaping.py`, `build.py`). |
| CrewAI Skills (Appendix A) | Reusable knowledge packs attached to agents (course Skill concept, Method 1 — per agent). | `skills/*/SKILL.md` knowledge packs + `src/bookgen/orchestration/skills.py`: `load_skills(agent_key)` discovers the packs under the parent `skills/` directory and returns **activated `Skill` objects** that `factory.create_agent` attaches to each real CrewAI `Agent` (per-agent attachment, course Method 1). |
| Validation | Guardrails that check correctness before later steps. | `src/bookgen/document/validators.py` and `ValidationReport` schema. |
| Observability | Visibility into what happened and why. | Intermediate artifacts, generated graph, validation reports, bibliography, test outputs, and `generated/intermediate/real_run_trace.json` for opt-in real runs. |
| LaTeX production | Turning content into professional PDF output. | `templates/latex/main.tex.j2`, implemented `src/bookgen/latex/renderer.py`, `compiler.py`, `escaping.py`, `build.py`, generated `.bib` and assets. |
| Language | The primary language and script direction of the document. | The document is primarily Hebrew (RTL) via `\setmainlanguage{hebrew}` / `\setmainfont{David CLM}`, ~3,260 Hebrew words across 6 chapters, with English kept inline only for technical terms; the `hebrew_english_section` is an explicit `\begin{english}` BiDi demo block, not the document's primary language. |

Quality and entry point: 134 tests pass, 2 skip, coverage ~94% (gate 85%), ruff 0 violations. The CLI is `uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main --dry-run [--build-pdf] [--run-crew]`. Running `--build-pdf` produces an 18-page Hebrew-primary `final.pdf`, and a snapshot copy is committed at the repository root so a grader sees it on clone.

## Specific Demonstrations

### Agent

The system defines agents through five distinct roles:

- Planner Agent
- Research Agent
- Writer Agent
- Reviewer Agent
- LaTeX Agent

Each agent exists because it owns a distinct part of the document-generation lifecycle.

### Task

Each agent has a task factory with a constrained expected output. The project avoids vague "do everything" prompts because the course emphasizes clear task decomposition.

### Crew

The crew is a small organization-like team. The design intentionally avoids adding agents such as Citation Agent or Visuals Agent because those responsibilities are deterministic.

### Process

The approved v1 process is sequential:

```text
Planner -> Research -> Writer -> Reviewer -> LaTeX
```

This matches the document dependency chain and keeps the first version easy to inspect.

### Context

Context is represented by structured files. For example:

```text
book_plan.json -> research_pack.json -> manuscript.md -> review_report.json -> latex_spec.json
```

The dry-run pipeline passes these task outputs through CrewAI-style context and persists them under `generated/intermediate/` for grading (`src/bookgen/orchestration/dry_run.py` and `crew.py`).

### Harness

The harness protects the project from fragile model output. It owns:

- configuration,
- schemas,
- validation,
- citation registry,
- graph generation,
- LaTeX rendering,
- PDF compilation,
- reporting.

### Tools/Skills

The course distinguishes model reasoning from reliable executable capabilities. This project follows that idea by keeping graph creation, citation handling, validation, LaTeX rendering, and PDF compilation in deterministic Python (`src/bookgen/latex/renderer.py`, `compiler.py`, `escaping.py`, `build.py`).

It also implements the CrewAI **Skills** concept directly (Appendix A, Method 1 — per agent): `skills/*/SKILL.md` define reusable knowledge packs, and `orchestration/skills.py::load_skills(agent_key)` discovers them and returns activated `Skill` objects that `factory.create_agent` attaches to each real CrewAI `Agent`. The packs cover LaTeX style, citation discipline, and course alignment.

### Validation

The validator checks:

- required artifacts,
- cover,
- table of contents,
- chapters,
- citations,
- image,
- graph,
- table,
- formula,
- Hebrew-English section.

### Observability

The project is designed so a grader can inspect:

- config files,
- intermediate artifacts,
- generated graph,
- generated bibliography,
- validation reports,
- tests,
- `generated/intermediate/real_run_trace.json` and `real_run_summary.json` for opt-in real runs.

### LaTeX Production

The system uses LaTeX templates and a deterministic compiler wrapper. The LaTeX Agent only produces assembly intent; Python renders the `.tex` (`renderer.py`) and compiles it (`compiler.py`, running `lualatex` -> `biber` -> `lualatex` -> `lualatex`). Rendering and PDF compilation are implemented, exercised by tests, and verified end-to-end: the compiled 18-page Hebrew-primary `final.pdf` is produced and committed at the repository root, with the cover, table of contents, embedded image, Python-generated graph, table, mathematical formula, Hebrew-English BiDi block, and the bibliography (3 citations resolved) all rendering correctly and 0 overfull boxes (no margin overflow). Reproducing the PDF from scratch requires a free TeX toolchain (`lualatex` + `biber`) plus the Hebrew `David CLM` font (culmus package); the default `--dry-run` path does not compile.
