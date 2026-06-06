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
| Guideline Compliance (docs + quality config) | Complete | `docs/PRD.md`, `PLAN.md`, `TODO.md`, `PROMPTS.md`, `PRD_latex_pipeline.md`, `PRD_citation_management.md`; `pyproject.toml` ruff + coverage config; `shared/version.py`; `.env-example`. `ruff check` passes (0 violations); 134 tests pass, 2 skip; coverage ~94% (gate 85%, pyproject fail_under=85) with `--cov`; `ruff format` clean; pre-commit hook (`scripts/hooks/pre-commit`) + CI (`.github/workflows/ci.yml`) added; README expanded (install/usage/config/license); `uv.lock` committed; all audit gap-closure items in `docs/TODO.md` are complete. |
| Real Execution Support (Milestone 5) | Complete | Real runs remain opt-in and API-key guarded (`--run-crew` + `OPENAI_API_KEY`). When enabled, `crew.kickoff()` runs through `ApiGatekeeper`, task outputs persist to `generated/intermediate/`, `real_run_trace.json` logs task inputs/outputs, token usage is extracted when CrewAI exposes it, and config-driven budget alerts come from `config/budgets.json`. |
| CrewAI Skills + build-skill | Complete | 3 `SKILL.md` knowledge packs under `skills/`, `orchestration/skills.py` discovery/assignment loader wired into agents (real-crew mode), unit tests; plus a Claude Code build skill at `.claude/skills/build-bookgen/`. |
| LaTeX Renderer + Compiler (Phase E) | Complete | `latex/escaping.py`, 5 Jinja templates, `latex/renderer.py` (Hebrew-primary `main.tex` plus `generated/latex/chapters/*.tex` — with cover/TOC/figures/table/formula/BiDi/bibliography), `latex/compiler.py` (multi-pass, graceful, UTF-8 log capture), `latex/build.py` wired into `main.py` (`--build-pdf`, renders **and compiles** end-to-end; emits `generated/pdf/final.pdf`). Build assets are copied into `generated/latex/assets/`, rendered citations are preflighted before compile, and the cover carries reconciled author/course/lecturer/date metadata. **Verified:** `--build-pdf` compiles an 18-page `final.pdf` (lualatex + biber, culmus `David CLM`). |
| SDK facade (Phase I) | Complete | `sdk/sdk.py` (`BookGenSDK`) is the single entry point for all business logic; `main.py` holds none and delegates to it. One CLI command now generates the graph, image, `references.bib`, and `main.tex`. |
| API Gatekeeper (Phase M / guideline 5) | Complete | `shared/gatekeeper.py` (rate limiting, retries, backpressure, monitoring) + versioned `config/rate_limits.json`; the real crew `kickoff` routes through it. `crew.py` split into `dry_run.py` to stay within the 150-line rule. |
| Research & Analysis (Phase L) | Complete | `research/sensitivity.py` (OAT page-count sensitivity) + `notebooks/sensitivity_analysis.ipynb` (LaTeX model + references); generates line/bar/scatter/box/heatmap figures (guideline 9.1-9.3). |
| Compliance hardening (guideline 7.3, 8.1, 13) | Complete | Runtime config-version validation (`load_config` fails on mismatch); `config/logging_config.json` wired via `logging.config.dictConfig`; `docs/ISO_25010.md` maps all 8 ISO/IEC 25010 quality characteristics. |
| Content (Phase G) | Complete | Deterministically authored **Hebrew-primary** 6-chapter manuscript (~3,260 Hebrew words, with English kept inline for technical terms — Agent, Task, Crew, Harness, validation…) in `data/intermediate/sample_book_plan.json`; renders to a full Hebrew-primary `main.tex` (Hebrew cover/TOC/chapter & section titles/captions, 6 chapters, figures, table, formula, and an explicit `\begin{english}` LTR block demonstrating the RTL↔LTR transition); the build generates `references.bib` (3 sources, included via `\nocite{*}`), and every chapter now renders an inline `\cite` (8 markers across 3 sources). **Verified in the compiled 18-page PDF:** cover, TOC, image, Python graph, table, formula, Hebrew-English BiDi, and the bibliography all render correctly — 0 overfull boxes, all citations resolve. |
| Real-run content path | Complete | Real CrewAI outputs now pass both schema validation and content-depth gates before replacing canonical artifacts. Shallow book plans, placeholder manuscripts, unapproved review reports, and incomplete LaTeX specs remain preserved under `generated/intermediate/real_raw/` for inspection while the deterministic canonical artifacts stay intact. A strong Markdown manuscript can drive rendered chapter prose; otherwise the renderer falls back to the curated BookPlan content. |

## Current State

Phase A through Phase M are complete. The optional operational choice is whether to spend money on a fresh API-backed CrewAI run; the delivered and tested default path remains deterministic and free.

LaTeX rendering is complete (`src/bookgen/latex/renderer.py` renders the full Hebrew-primary `main.tex`; `build.py` wires it into the CLI). PDF compilation is also COMPLETE: `--build-pdf` compiles a verified 18-page Hebrew-primary `final.pdf` end-to-end (lualatex + biber, culmus `David CLM`), with 0 overfull boxes and all citations resolved; a snapshot copy is committed at the repo root. Reproducing the PDF from scratch still requires a free TeX toolchain — lualatex+biber — with the culmus package; the default `--dry-run` path does not compile.

### Recent hardening

- **Skills attach to real agents.** `orchestration/skills.py::load_skills(agent_key)` discovers the `skills/*/SKILL.md` packs and returns activated `Skill` objects that `factory.create_agent` attaches per-agent to the real CrewAI `Agent` (course Method 1). The earlier leaf-dir string paths that were silently dropped are fixed.
- **Gatekeeper thread-safe + richer limits.** `shared/gatekeeper.py` now uses `threading.Lock` + `Semaphore`, enforces per-minute **and** per-hour limits plus `concurrent_max`, and documents a synchronous block-until-reset overflow model with `BackpressureError` at `max_queue_depth`.
- **models.json wired into real runs.** `config/models.json` drives per-agent model/temperature (factory builds the LLM) and carries a `pricing` block for `gpt-4o-mini`, `gpt-4o`, and `claude-sonnet-4-6`.
- **SDK extension hooks.** `sdk/sdk.py` exposes `before_<stage>`/`after_<stage>` callables around `run_crew`/`generate_assets`/`build_document`, a `STAGES` registry (guideline 12), and `estimate_cost()` for a dry-run cost forecast.
- **Parallel utilities + concurrent figures.** `shared/parallel.py` adds `parallel_map` (threads) and `cpu_parallel_map` (processes); the six sensitivity figures now render concurrently (guideline 15).
- **Cost estimator + pricing.** `accounting.py::estimate_tokens`/`estimate_cost_usd` plus the `config/models.json` pricing block back `SDK.estimate_cost()`.
- **setup.json versioned.** `config/setup.json` carries a top-level `"version": "1.00"` validated at runtime alongside the other configs.
- **LaTeX headers/footers + Hebrew mono fix.** `templates/latex/main.tex.j2` defines Hebrew fonts (incl. `\setmonofont` + `\hebrewfonttt`) before `\setmainlanguage{hebrew}` (fixes a polyglossia Hebrew-monospace error), adds fancyhdr headers/footers, and fixes `\graphicspath`.
- **Compiler error scanning.** `compiler.scan_log_issues` now flags any `! ... Error` line in the build log.
- **Markdown intro/inline handling.** `latex/markdown_manuscript.py` preserves prose before the first chapter as an intro section and converts `**bold**`/`*italic*`/`- ` lists to LaTeX.
- **Sixth (waterfall) figure + executed notebook.** `research/sensitivity.py` + `sensitivity_plots.py` now produce six figures with a colorblind-safe Okabe-Ito palette, labeled axes/legends, a finite-difference `partial_sensitivity()` index, and `compare_baselines()`; `notebooks/sensitivity_analysis.ipynb` is executed and committed with outputs.

## Milestone numbering

Two milestone numbering schemes exist in the docs and they diverge after milestone 4 (T474). This note records the **canonical mapping** so neither file is renumbered wholesale:

- `docs/PROJECT_BLUEPRINT.md` §9 is the **canonical roadmap** and uses a 9-step scale (0–8): 5 = Sequential crew execution, 6 = LaTeX rendering, 7 = PDF compilation, 8 = Polish/tests/submission.
- This file's roadmap table splits the Blueprint's milestone 5 into two rows — 5 (Sequential Crew Execution) and 6 (Artifact Generation) — which shifts the later numbers by one: LaTeX rendering = 7, PDF compilation = 8, Submission polish = 9.

Canonical mapping (Blueprint ↔ this file's roadmap table):

| Topic | Blueprint §9 | This file's roadmap table |
|---|---|---|
| Sequential crew execution + artifact persistence | 5 | 5 + 6 |
| LaTeX rendering | 6 | 7 |
| PDF compilation | 7 | 8 |
| Polish / submission | 8 | 9 |

When citing a milestone number across documents, prefer the **Blueprint §9** numbering. The completed milestones 0–4 are identical in both files.

## Completed Roadmap Milestones

| Milestone | Goal | Notes |
|---|---|---|
| 5. Sequential Crew Execution | Add controlled non-dry-run execution and artifact persistence. | Complete — opt-in and API-key guarded, routed through the gatekeeper. |
| 6. Artifact Generation | Persist real intermediate outputs from task results. | Complete — writes runtime artifacts and `real_run_trace.json` to `generated/intermediate/`; keeps `sample_` files as committed examples. |
| 7. LaTeX Rendering | Render `.tex` files from templates. | Complete — `latex/renderer.py` renders `main.tex` plus per-chapter `.tex` files from the CLI. |
| 8. PDF Compilation | Compile final PDF with LuaLaTeX/XeLaTeX and bibliography backend. | Complete — `--build-pdf` compiles an 18-page Hebrew-primary `final.pdf` (lualatex+biber, culmus David CLM); build log captured at `generated/latex/build.log`. |
| 9. Submission Polish | README evidence, tests, final cleanup. | Complete — grader walkthrough, screenshots, final PDF snapshot, and clean TODO are present. |

## Current Test Command

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with pytest --with pytest-cov --with matplotlib --with jinja2 python -m pytest tests --cov=bookgen
```

Known passing result:

```text
134 passed, 2 skipped, ~94% coverage
```

Coverage: ~94% (gate 85%, pyproject `fail_under=85`).

## Current CLI

```powershell
uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main --dry-run [--build-pdf] [--run-crew]
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
| Rendered LaTeX project | `generated/latex/main.tex` and `generated/latex/chapters/*.tex` |
| Copied build assets | `generated/latex/assets/` |
| Bibliography | `data/references/references.bib` |

A committed `references.bib` copy is tracked for grader visibility; other `data/references/` artifacts are generated from `data/input/source_registry.json` and git-ignored.

## Operational Notes

- Real LLM run support is implemented but remains opt-in via `--run-crew` (needs `OPENAI_API_KEY`); default is dry-run.
- No code blockers remain. `--build-pdf` compiles an 18-page Hebrew-primary `final.pdf` end-to-end (verified with MiKTeX lualatex + biber and the culmus `David CLM` font). A grader needs only a TeX toolchain with the culmus package; a snapshot `final.pdf` is committed at the repo root.

## Status Rules

When later milestones or scope changes are completed:

1. Update this file.
2. Update `docs/PROJECT_BLUEPRINT.md` if the project vision changes.
3. Add or update tests.
4. Keep README short and point to docs.

