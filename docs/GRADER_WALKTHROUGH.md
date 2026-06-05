# Grader Walkthrough

A concise, step-by-step guide for evaluating this project. It covers install,
the safe dry-run, rendering and compiling the PDF, where the final PDF lives,
how to run the tests, and a checklist mapping every assignment requirement to
where it appears in the committed 18-page PDF.

> TL;DR — nothing needs to be built to grade the deliverable: the final PDF is
> **already committed at the repository root as `final.pdf`** (a copy of
> `generated/pdf/final.pdf`). Open it directly. The steps below let you reproduce
> it and inspect the pipeline.

## 0. Prerequisites

- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/) (package manager / runner)
- PowerShell (Windows) or any POSIX shell
- **Only to recompile the PDF:** a free LaTeX toolchain (MiKTeX or TeX Live) with
  `lualatex` + `biber`, and the Hebrew font **David CLM** from the
  [culmus](https://culmus.sourceforge.io/) package. None of this is needed to
  read the committed `final.pdf` or to run the dry-run and tests.

## 1. Install

```powershell
git clone https://github.com/AmrSafadi/AI-Agent-Orchestration-HW3.git
cd <path-to>\AI-Agent-Orchestration-HW3
uv sync            # resolve/install dependencies into a local env
```

`uv sync` uses the committed `uv.lock`. No secrets are required for the default
dry-run path; `.env` is only needed for a real (paid) `--run-crew` run, which is
intentionally not exercised under this project's no-paid-API constraint.

## 2. Run The Dry-Run (no API, safe default)

The dry-run loads config, assembles the five-agent sequential crew **without
calling `crew.kickoff()`**, persists the intermediate artifacts, and renders the
full LaTeX project. It never contacts any LLM provider and costs nothing.

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main --dry-run
```

Expected (abridged):

```text
BookGen configuration loaded successfully.
Execution mode: DRY-RUN (default). CrewAI kickoff will not be called.
Crew assembled: 5 agents, 5 tasks, process=sequential.
Dry-run completed. CrewAI kickoff was not called.
Rendered LaTeX project: ...\generated\latex\main.tex
LaTeX render status: OK (PDF compile skipped; run with --build-pdf ...).
```

Dry-run artifacts land in `generated/intermediate/` (`book_plan.json`,
`research_pack.json`, `manuscript.md`, `review_report.json`, `latex_spec.json`).
The committed `data/intermediate/sample_*` files are the curated examples.

## 3. Render + Compile The PDF (optional — needs a TeX toolchain)

The dry-run already renders `generated/latex/main.tex`. To also compile the PDF,
add `--build-pdf` (requires the toolchain from step 0):

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main --dry-run --build-pdf
```

The compiler runs `lualatex -> biber -> lualatex -> lualatex` and degrades
gracefully if the toolchain is absent (it reports a skipped compile rather than
failing). The document is **primarily Hebrew (RTL)** via `\setmainlanguage{hebrew}`
and `\setmainfont{David CLM}`, with English kept inline only for technical terms.
Successful compilation writes `generated/pdf/final.pdf` and a build log to
`generated/latex/build.log`.

## 4. Where The Final PDF Is

- **`final.pdf`** — committed snapshot at the **repository root** (open this to grade).
- `generated/pdf/final.pdf` — the build output the root copy is taken from.

It is an 18-page, Hebrew-primary PDF, verified to compile end-to-end with
`lualatex` + `biber` and the culmus `David CLM` font: 0 overfull boxes, no
undefined references, all citations resolved.

## 5. Run The Tests

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with pytest --with pytest-cov --with matplotlib --with jinja2 python -m pytest tests --cov=bookgen
```

Expected: **89 passed**, coverage **92.46%** against an 85% gate
(`pyproject.toml` `fail_under=85`). Lint is clean:

```powershell
uv run --no-project --with ruff ruff check .
```

Expected: **0 violations** (and `ruff format .` reports no changes).

## 6. Assignment Requirement Checklist (mapping to the 18-page PDF)

Every required feature is present in the committed `final.pdf`. The PDF is
Hebrew-primary, so headings/captions are in Hebrew; English appears inline only
for technical terms and in the explicit BiDi demo block.

| # | Assignment requirement | Where it appears in `final.pdf` | Source in repo |
|---|---|---|---|
| 1 | Multiple specialized agents | Reflected in the pipeline graph and chapter content | `src/bookgen/orchestration/agents.py` (5 agents) |
| 2 | CrewAI orchestration | Sequential crew assembled in the dry-run | `src/bookgen/orchestration/crew.py`, `dry_run.py` |
| 3 | Professional PDF generation | The whole 18-page document | `src/bookgen/latex/renderer.py`, `compiler.py` |
| 4 | Cover page | Page 1 — title, author, course, lecturer, date | `templates/latex/main.tex.j2` (cover block) |
| 5 | Table of contents | Page 2 (after the cover) | `\tableofcontents` in `main.tex.j2` |
| 6 | At least ~15 pages | 18 pages total | 6 chapters in `data/intermediate/sample_book_plan.json` |
| 7 | Image | Embedded figure in the body | `templates/latex/chapter.tex.j2` (figure), `harness/assets.py` |
| 8 | Python-generated graph | `agent_pipeline_graph.png` figure | `src/bookgen/harness/graph_generator.py` (matplotlib) |
| 9 | Table | Rendered table inside a chapter | `templates/latex/chapter.tex.j2` (table block) |
| 10 | Mathematical formula | Displayed equation inside a chapter | `templates/latex/chapter.tex.j2` (formula block) |
| 11 | Hebrew–English mixed (BiDi) | Explicit `\begin{english}` LTR block within the Hebrew (RTL) body | `chapter.tex.j2` `hebrew_english_section` |
| 12 | Bibliography and citations | Bibliography page; 8 inline `\cite` markers across 3 sources | `harness/citations.py` -> `references.bib`, `\nocite{*}` |
| 13 | Final PDF output | `final.pdf` at the repo root | `generated/pdf/final.pdf` |

## 7. Visual Evidence

Rendered pages from the committed `final.pdf` (PNGs under `docs/screenshots/`):

| Page | Screenshot | Shows |
|---|---|---|
| Cover | `docs/screenshots/cover.png` | Hebrew title + author/course/lecturer/date (BiDi) |
| Chapter 1 | `docs/screenshots/chapter1.png` | Hebrew prose with inline English technical terms |
| Features | `docs/screenshots/features.png` | Embedded image, Python graph, and the `\begin{english}` BiDi block |
| Table | `docs/screenshots/table.png` | Booktabs table (RTL) of agent roles |
| Bibliography | `docs/screenshots/bibliography.png` | Resolved numbered citations |

Notes for the grader:

- The canonical authored manuscript is `data/intermediate/sample_book_plan.json`
  (the BookPlan / `book_plan.json` contract) that the renderer renders from;
  `sample_manuscript.md` is only an auxiliary sample.
- The pipeline is single-threaded and synchronous **by design** for determinism
  and reproducibility (see `docs/PARALLELISM.md` for the thread-safety stance and
  how concurrency could be added safely).
- Course-concept mapping: `docs/COURSE_ALIGNMENT.md`. Live status and milestone
  numbering: `docs/IMPLEMENTATION_STATUS.md`. Full vision: `docs/PROJECT_BLUEPRINT.md`.
