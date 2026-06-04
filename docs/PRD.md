# Product Requirements Document (PRD)

Mandatory document per submission guideline 2.2. This is the central
requirements document for the project. Architecture and design live in
[PLAN.md](PLAN.md); task tracking lives in [TODO.md](TODO.md).

## 1. Overview and Context

**Product:** `bookgen` — a CrewAI-based article/book generator that produces a
professional, LaTeX-compiled PDF.

**Problem.** A naive "ask one model to write a book and make a PDF" prompt is
unreliable: it mixes reasoning-heavy work (planning, writing, reviewing) with
fragile deterministic work (BibTeX keys, LaTeX escaping, multi-pass
compilation), and it produces results that cannot be reproduced or audited.

**Approach.** Decompose the task into a small, sequential CrewAI team of five
specialized agents for the reasoning work, and a deterministic Python *harness*
for the work that must be exact. Agents decide *intent*; Python executes
*reliably*.

**Target audience.**
- The course grader evaluating assignment and guideline compliance.
- Teammates and future AI assistants continuing the implementation.

## 2. Goals and Success Metrics

| Goal | Metric / Acceptance Criterion |
|---|---|
| Demonstrate CrewAI orchestration | Five specialized agents, five context-linked tasks, `Process.sequential`. |
| Produce a professional PDF | A compiled PDF containing every required feature (see §3). |
| Keep the system safe to run | Dry-run is the default; no API call or spend without explicit `--run-crew` + key. |
| Meet engineering standards | Ruff = 0 violations; test coverage ≥ 85%; files ≤ 150 code lines; `uv` only. |
| Reproducibility & observability | Structured intermediate artifacts, validation report, build log. |

## 3. Functional Requirements

### 3.1 Assignment deliverables (the graded PDF must contain)

1. Multiple specialized agents and CrewAI orchestration.
2. Cover page (topic, author, date, course, lecturer).
3. Table of contents with headers/footers.
4. Chapters and sections, **≥ 15 pages**.
5. At least one image.
6. At least one Python-generated graph.
7. At least one table.
8. At least one mathematical formula (typeset, not plain text).
9. A Hebrew–English bidirectional (BiDi) chapter with correct LTR/RTL handling.
10. A bibliography with relevant citations.
11. A final PDF output compiled with LuaLaTeX (XeLaTeX fallback).

### 3.2 System behavior

- Load versioned configuration from `config/*.json`.
- Assemble a sequential crew (Planner → Research → Writer → Reviewer → LaTeX).
- Pass each task's output to the next as `context`.
- Persist structured artifacts (`book_plan`, `research_pack`, `manuscript`,
  `review_report`, `latex_spec`) under `generated/intermediate/`.
- Run deterministic harness steps: citation/BibTeX generation, graph generation,
  document validation, LaTeX rendering, PDF compilation.

## 4. Non-Functional Requirements

- **Safety:** default execution must not call any external API or spend tokens.
- **Quality:** zero Ruff violations; ≥ 85% coverage; each code file ≤ 150 lines.
- **Security:** no secrets in source; secrets via environment variables only;
  `.env-example` committed with dummy values (guideline 7.4).
- **Tooling:** `uv` is the only package manager/runner; `pyproject.toml` is the
  single source of dependencies; `uv.lock` committed.
- **Maintainability:** SDK-style single entry point, OOP, no code duplication.
- **Portability:** relative paths; runs on Windows (PowerShell) with `uv`.

## 5. User Stories

- *As a grader,* I can clone the repo and run a safe dry-run with no key, then
  inspect the generated artifacts and the final PDF, to verify every requirement.
- *As a teammate,* I can read `docs/` and understand the system before touching code.
- *As a user,* I can provide a topic in config and produce a professional PDF.

## 6. Assumptions, Dependencies, Out of Scope

**Assumptions.** A LaTeX toolchain (LuaLaTeX + biber) is available for the
compilation milestone; an OpenAI-compatible key is available only for the
optional real-crew milestone.

**Dependencies.** `crewai`, `pydantic`, `jinja2`, `matplotlib`, `python-dotenv`;
a TeX distribution (MiKTeX/TeX Live) for PDF compilation.

**Out of scope (v1).** Hierarchical CrewAI process; additional agents beyond the
approved five; autonomous source retrieval/RAG; a cost dashboard; a GUI.

## 7. Timeline and Milestones

See [TODO.md](TODO.md) and `docs/IMPLEMENTATION_STATUS.md` for live status. In
summary: planning, skeleton, config/schemas, deterministic harness, and CrewAI
definitions with dry-run are complete; LaTeX rendering, PDF compilation, optional
real-crew execution, and submission polish remain.

## 8. Specialized Mechanism PRDs

Per guideline 2.3, central mechanisms have dedicated PRDs:

- [PRD_latex_pipeline.md](PRD_latex_pipeline.md) — LaTeX rendering and PDF compilation.
- [PRD_citation_management.md](PRD_citation_management.md) — citation registry and BibTeX generation.
