---
name: build-bookgen
description: Implement the next phase/milestone of the AI-Agent-Orchestration-HW3 "bookgen" CrewAI + LaTeX project, following the repo's guideline-aligned workflow (TODO phases, ruff/format, tests + 85% coverage, docs sync, commit on request). Use when the user asks to build, continue, or implement a phase, milestone, or task of this project.
---

# Build BookGen

Implements the next unit of work on the `bookgen` project while keeping it aligned
to the submission guidelines and the `docs/` always in sync.

## 1. Before coding
1. Read `materials/software_submission_guidelines-V3_Summary.md` (the grading rubric),
   plus `docs/PLAN.md` and `docs/PRD.md`.
2. Open `docs/TODO.md`, locate the next unchecked phase/tasks (stable `T###` ids).
3. Read the real source files you will touch — never assume their contents.

## 2. While coding
- Every code file stays ≤ 150 non-blank/non-comment lines; split modules if needed.
- No hardcoded paths or secrets; configurable values live in `config/*.json`;
  secrets come from environment variables only.
- Keep the **dry-run path the default**. Never call an LLM/API or compile a PDF
  unless the user explicitly approves that milestone.
- Do not add agents beyond the approved five; keep deterministic components
  (citations, graph, validators, renderer, compiler) deterministic.

## 3. Verify — all must pass before declaring done
```
uv run --no-project --with ruff ruff format .
uv run --no-project --with ruff ruff check .            # 0 violations
PYTHONPATH=src uv run --no-project --with pydantic --with pytest --with pytest-cov --with matplotlib python -m pytest tests --cov --cov-fail-under=85
```

## 4. After coding — ALWAYS
- Update every affected file under `docs/`:
  - `TODO.md`: tick the relevant checkboxes and fix the `Total tasks` count line.
  - `IMPLEMENTATION_STATUS.md`: reflect what is now complete / in progress.
  - `PLAN.md` / `PRD.md` / per-mechanism PRDs: update if architecture or
    requirements changed. `COSTS.md` / `USAGE.md` if relevant.
- Summarize changed files plus the test/coverage result.
- Commit only when the user asks, with a meaningful message and a
  `Co-Authored-By: Claude` trailer; push to the `Sharbel` branch and offer a PR.

## 5. Reference map
- Phases & tasks: `docs/TODO.md`. Architecture & ADRs: `docs/PLAN.md`.
- Agent/task design: `AGENTS_DESIGN.md`, `TASK_FLOW.md`. Folder rules: `FOLDER_STRUCTURE.md`.
- Source layout: `src/bookgen/{shared,document,harness,orchestration,latex}/`.
