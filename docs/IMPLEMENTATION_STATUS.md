# Implementation Status

This document tracks what is complete, what is in progress, and what remains.

## Completed Milestones

| Milestone | Status | Evidence |
|---|---|---|
| 0. Planning | Complete | Root planning documents: `PROJECT_PLAN.md`, `ARCHITECTURE.md`, `AGENTS_DESIGN.md`, `TASK_FLOW.md`, `FOLDER_STRUCTURE.md`. |
| 1. Skeleton | Complete | `README.md`, `pyproject.toml`, config files, package folders, placeholder modules. |
| 2. Config and Schemas | Complete | `shared/config.py` (all configs carry a `version`), `shared/logging.py`, `document/schemas.py` + `document/report_schemas.py` — 10 artifact contracts with validators, documented examples, and round-trip tests. |
| 3. Deterministic Harness | Complete | `graph_generator.py`, `citations.py` + `citation_report.py`, `validators.py` (+ latex-spec file checks), `assets.py`, `evidence.py`; headless Agg backend (`_mpl.py`); sample data, tests. (Phase C complete; a committed `references.bib` copy is now tracked for grader visibility.) |
| Documentation | Complete | `docs/PROJECT_BLUEPRINT.md`, `COURSE_ALIGNMENT.md`, `IMPLEMENTATION_STATUS.md`, `ARCHITECTURE_DIAGRAM.md`, `QUICK_START.md`, `CONTRIBUTING.md`. |
| 4. CrewAI Definitions | Complete | `agents.py`, `tasks.py`, `build_crew()`, `run_crew()`, CLI dry-run mode, generated intermediate artifacts, orchestration tests. |
| Guideline Compliance (docs + quality config) | Partial | `docs/PRD.md`, `PLAN.md`, `TODO.md`, `PROMPTS.md`, `PRD_latex_pipeline.md`, `PRD_citation_management.md`; `pyproject.toml` ruff + coverage config; `shared/version.py`; `.env-example`. `ruff check` passes (0 violations); 77 tests pass; coverage 93.41% (gate 85%, pyproject fail_under=85) with `--cov`; `ruff format` clean; pre-commit hook (`scripts/hooks/pre-commit`) + CI (`.github/workflows/ci.yml`) added; README expanded (install/usage/config/license); `uv.lock` committed; config files now carry `version` keys (Phase A complete). Remaining: audit gap-closure items (API gatekeeper, rate limits, LICENSE, validator hardening, runtime config-version validation) tracked in `docs/TODO.md` Phase M. |
| CrewAI Skills + build-skill | Complete | 3 `SKILL.md` knowledge packs under `skills/`, `orchestration/skills.py` discovery/assignment loader wired into agents (real-crew mode), unit tests; plus a Claude Code build skill at `.claude/skills/build-bookgen/`. |
| LaTeX Renderer + Compiler (Phase E) | Complete | `latex/escaping.py`, 5 Jinja templates, `latex/renderer.py` (Hebrew-primary `main.tex` — `\setmainlanguage{hebrew}` / `\setotherlanguage{english}` — with cover/TOC/figures/table/formula/BiDi/bibliography), `latex/compiler.py` (multi-pass, graceful, UTF-8 log capture), `latex/build.py` wired into `main.py` (`--build-pdf`, renders **and compiles** end-to-end; emits `generated/pdf/final.pdf`). Cover carries author/course/lecturer/date; `\graphicspath` resolves assets at compile time. **Verified:** `--build-pdf` compiles an 18-page `final.pdf` (lualatex + biber, culmus `David CLM`). Optional remaining: per-chapter `.tex` files and the xelatex fallback. |
| SDK facade (Phase I) | Complete | `sdk/sdk.py` (`BookGenSDK`) is the single entry point for all business logic; `main.py` holds none and delegates to it. One CLI command now generates the graph, image, `references.bib`, and `main.tex`. |
| API Gatekeeper (Phase M / guideline 5) | Complete | `shared/gatekeeper.py` (rate limiting, retries, backpressure, monitoring) + versioned `config/rate_limits.json`; the real crew `kickoff` routes through it. `crew.py` split into `dry_run.py` to stay within the 150-line rule. |
| Research & Analysis (Phase L) | Complete | `research/sensitivity.py` (OAT page-count sensitivity) + `notebooks/sensitivity_analysis.ipynb` (LaTeX model + references); generates line/bar/scatter/box/heatmap figures (guideline 9.1-9.3). |
| Compliance hardening (guideline 7.3, 8.1, 13) | Complete | Runtime config-version validation (`load_config` fails on mismatch); `config/logging_config.json` wired via `logging.config.dictConfig`; `docs/ISO_25010.md` maps all 8 ISO/IEC 25010 quality characteristics. |
| Content (Phase G) | Mostly complete | Deterministically authored **Hebrew-primary** 6-chapter manuscript (~3,260 Hebrew words, with English kept inline for technical terms — Agent, Task, Crew, Harness, validation…) in `data/intermediate/sample_book_plan.json`; renders to a full Hebrew-primary `main.tex` (Hebrew cover/TOC/chapter & section titles/captions, 6 chapters, figures, table, formula, and an explicit `\begin{english}` LTR block demonstrating the RTL↔LTR transition); the build generates `references.bib` (3 sources, included via `\nocite{*}`), and every chapter now renders an inline `\cite` (8 markers across 3 sources). **Verified in the compiled 18-page PDF:** cover, TOC, image, Python graph, table, formula, Hebrew-English BiDi, and the bibliography all render correctly — 0 overfull boxes, all citations resolve. |

## In Progress

Phase A (configuration) and Phase B (schemas — 10 artifact contracts with validators, documented examples, and round-trip tests; added `report_schemas.py`) are complete. Submission-guideline compliance is being hardened (mandatory docs + quality config) as a non-numbered track. See `docs/TODO.md` Phase I (Compliance) for the remaining compliance items, and Phase M for additional gaps found in a materials-vs-repo re-audit (API gatekeeper / rate-limits / queue, `LICENSE` + `license` metadata, `config/logging_config.json`, runtime config-version validation, validator false-green fix, sub-package `__init__.py`, agent-security / red-team).

LaTeX rendering is complete (`src/bookgen/latex/renderer.py` renders the full Hebrew-primary `main.tex`; `build.py` wires it into the CLI). The remaining milestones are PDF compilation (blocked only on installing a free TeX toolchain — lualatex+biber — plus a Hebrew font such as David CLM) and submission polish.

## Future Milestones

| Milestone | Goal | Notes |
|---|---|---|
| 5. Sequential Crew Execution | Add controlled non-dry-run execution and artifact persistence. | Must remain opt-in and API-key guarded. |
| 6. Artifact Generation | Persist real intermediate outputs from task results. | Write runtime artifacts to `generated/intermediate/`; keep `sample_` files as committed examples. |
| 7. LaTeX Rendering | Render `.tex` files from templates. | Complete — `latex/renderer.py` renders the full Hebrew-primary `main.tex` end-to-end from the CLI. |
| 8. PDF Compilation | Compile final PDF with LuaLaTeX/XeLaTeX and bibliography backend. | Complete — `--build-pdf` compiles an 18-page Hebrew-primary `final.pdf` (lualatex+biber, culmus David CLM); build log captured at `generated/latex/build.log`. |
| 9. Submission Polish | README evidence, tests, final cleanup. | Remaining — prepare course-grader walkthrough. |

## Current Test Command

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with pytest --with pytest-cov --with matplotlib --with jinja2 python -m pytest tests --cov=bookgen
```

Known passing result (through Phase E):

```text
77 passed
```

Coverage: 93.41% (gate 85%, pyproject `fail_under=85`).

## Current CLI

```powershell
python -m bookgen.main --dry-run [--build-pdf] [--run-crew]
```

Dry-run is the default and never calls the API; `--run-crew` needs `OPENAI_API_KEY`. A console script `bookgen` is also installed.

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

A committed `references.bib` copy is tracked for grader visibility; other `data/references/` artifacts are generated from `data/input/source_registry.json` and git-ignored.

## Not Yet Implemented

- Real LLM run is opt-in via `--run-crew` (needs `OPENAI_API_KEY`); default is dry-run.
- No code blockers remain. `--build-pdf` compiles an 18-page Hebrew-primary `final.pdf` end-to-end (verified with MiKTeX lualatex + biber and the culmus `David CLM` font). A grader needs only a TeX toolchain with the culmus package; a snapshot `final.pdf` is committed at the repo root.

## Status Rules

When future milestones are completed:

1. Update this file.
2. Update `docs/PROJECT_BLUEPRINT.md` if the project vision changes.
3. Add or update tests.
4. Keep README short and point to docs.

