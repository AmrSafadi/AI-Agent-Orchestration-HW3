# Course Alignment

This document maps course concepts to concrete project components.

| Course concept | Meaning in course context | Project component |
|---|---|---|
| Agent | A specialized worker with role, goal, backstory, and possible tools. | `src/bookgen/orchestration/agents.py` defines Planner, Research, Writer, Reviewer, and LaTeX agent factories. |
| Task | A measurable work unit with description and expected output. | `src/bookgen/orchestration/tasks.py` defines plan, research, writing, review, and LaTeX-spec task factories. |
| Crew | The team that combines agents and tasks. | `src/bookgen/orchestration/crew.py` assembles the five-agent crew with dry-run safety. |
| Process | The execution strategy for the crew. | Version 1 uses `Process.sequential`, configured through `config/setup.json`. |
| Context | Output from one task passed to later tasks. | Structured artifacts: `book_plan.json`, `research_pack.json`, `manuscript.md`, `review_report.json`, `latex_spec.json`. |
| Harness | The software system around the model. | `src/bookgen/shared`, `src/bookgen/document`, `src/bookgen/harness`, `src/bookgen/latex`. |
| Tools/Skills | Reliable capabilities that support agents. | Deterministic CitationManager, GraphGenerator, Validator, future LaTeX Renderer and PDFCompiler. |
| Validation | Guardrails that check correctness before later steps. | `src/bookgen/document/validators.py` and `ValidationReport` schema. |
| Observability | Visibility into what happened and why. | Intermediate artifacts, generated graph, validation reports, bibliography, test outputs, future logs. |
| LaTeX production | Turning content into professional PDF output. | `templates/latex/main.tex.j2`, future `renderer.py`, future `compiler.py`, generated `.bib` and assets. |

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

The real implementation will pass these task outputs through CrewAI context and persist them for grading.

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

The course distinguishes model reasoning from reliable executable capabilities. This project follows that idea by keeping graph creation, citation handling, and validation in Python.

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
- future CrewAI verbose logs.

### LaTeX Production

The final system will use LaTeX templates and a deterministic compiler wrapper. The LaTeX Agent only produces assembly intent; Python will render and compile.
