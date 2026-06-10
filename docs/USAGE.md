# Usage & Interface (UI/UX)

Required by the documentation and UI/UX standards. The system is a command-line
tool (no GUI); this document lets a reader understand the experience **without
running it**.

## 1. Interface type

A single CLI entry point, `bookgen.main`, run via `uv`. There is no graphical
interface; all interaction is through flags and printed status output.

## 2. Commands & modes

Set `$env:PYTHONPATH="src"` first (PowerShell).

All commands share the prefix `uv run --no-project --with pydantic --with
matplotlib --with jinja2 python -m bookgen.main` (abbreviated `… python -m
bookgen.main` below).

| Goal | Command | Calls API? |
|---|---|---|
| Startup check (default) | `uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main` | No |
| Explicit dry-run | `… python -m bookgen.main --dry-run` | No |
| Render + build PDF | `… python -m bookgen.main --build-pdf` (renders `main.tex`, then compiles the PDF; needs a TeX toolchain) — verified to produce a 19-page `final.pdf` (lualatex + biber, culmus David CLM); a committed snapshot is at the repo root | No |
| Cost forecast | `… python -m bookgen.main --estimate-cost` (prints a config-driven token/USD forecast, then exits) | No |
| Real crew run | `… python -m bookgen.main --run-crew` (needs `OPENAI_API_KEY`) | Yes |
| Run tests | `uv run --no-project --with pydantic --with pytest --with pytest-cov --with matplotlib --with jinja2 python -m pytest tests --cov=bookgen` | No |

`--dry-run` and `--run-crew` are mutually exclusive; dry-run is the default.
The installed `bookgen` console script is an equivalent alternative to
`python -m bookgen.main` (e.g. `bookgen --dry-run --build-pdf`).

## 3. What the user sees (sample dry-run session)

```text
BookGen configuration loaded successfully.
Project title: AI Agent Orchestration HW3
Topic: Football Analytics and AI-Based Match Strategy
Output directory: ...\generated
Execution mode: DRY-RUN (default).
Crew assembled: 5 agents, 5 tasks, process=sequential.
Dry-run completed. CrewAI kickoff was not called.
Rendered LaTeX project: <root>\generated\latex\main.tex
Rendered main.tex (LaTeX compilation not requested).
```

## 4. UX qualities (Nielsen's ten usability heuristics)

All ten heuristics, each mapped to the CLI:

1. **Visibility of system status:** every run prints loaded config, project
   title/topic, output directory, execution mode, crew composition, and an
   explicit completion line, so the user always knows what happened.
2. **Match between system and the real world:** vocabulary mirrors the course
   domain (agents, tasks, crew, process, dry-run, render, compile) rather than
   internal jargon.
3. **User control and freedom:** explicit, mutually exclusive mode flags
   (`--dry-run` / `--run-crew`) and an opt-in `--build-pdf`; nothing irreversible
   or costly happens without a flag.
4. **Consistency and standards:** standard POSIX-style `--flags`, conventional
   exit codes (0 success, 1 failure), and the same `uv run … python -m
   bookgen.main` invocation everywhere; the console script `bookgen` behaves
   identically.
5. **Error prevention:** dry-run is the safe default; the paid path requires
   **both** `--run-crew` and `OPENAI_API_KEY`; mutually exclusive flags prevent
   contradictory modes; config is validated up front before any work runs.
6. **Recognition rather than recall:** `--help` lists every flag and mode, so the
   user recognizes options instead of memorizing them; printed status echoes the
   active mode.
7. **Flexibility and efficiency of use:** run a single stage or the full
   pipeline; the short `bookgen` console script is the power-user shortcut for the
   long `uv run` form.
8. **Aesthetic and minimalist design:** output is a handful of plain, scannable
   status lines — no noise, no progress spam.
9. **Help users recognize, diagnose, and recover from errors:** failures surface
   a single clear message (e.g. missing `OPENAI_API_KEY`, missing config/version,
   absent TeX toolchain) plus where to look (`build.log`), and the missing-key /
   missing-toolchain cases tell the user exactly what to do next.
10. **Help and documentation:** `--help`, this `docs/USAGE.md`, `QUICK_START.md`,
    and the troubleshooting section in `README.md` cover setup, commands, and
    common errors.

## 4a. CLI session transcripts (per state)

**State 1 — default dry-run (no API, no toolchain needed):**

```text
$ uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main
BookGen configuration loaded successfully.
Project title: AI Agent Orchestration HW3
Topic: Football Analytics and AI-Based Match Strategy
Output directory: ...\generated
Execution mode: DRY-RUN (default).
Crew assembled: 5 agents, 5 tasks, process=sequential.
Dry-run completed. CrewAI kickoff was not called.
Rendered LaTeX project: ...\generated\latex\main.tex
Rendered main.tex (LaTeX compilation not requested).
# exit code 0
```

**State 2 — `--dry-run --build-pdf` with no TeX toolchain (graceful skip):**

```text
$ uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main --dry-run --build-pdf
BookGen configuration loaded successfully.
Execution mode: DRY-RUN (default).
Dry-run completed. CrewAI kickoff was not called.
Rendered LaTeX project: ...\generated\latex\main.tex
PDF compilation skipped: lualatex not found on PATH. See generated/latex/build.log.
# exit code 0  (main.tex still rendered; the reason is logged, nothing crashes)
```

**State 3 — `--run-crew` without `OPENAI_API_KEY` (clean error):**

```text
$ uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main --run-crew
BookGen configuration loaded successfully.
Execution mode: REAL CREW (--run-crew).
Error: OPENAI_API_KEY is required for --run-crew. Set it in your environment or .env.
# exit code 1  (no provider call attempted)
```

## 5. Outputs the user can inspect

After a run: the rendered LaTeX project at `generated/latex/main.tex` (the key
rendered deliverable); artifacts under `generated/intermediate/` (`book_plan`,
`research_pack`, `manuscript`, `review_report`, `latex_spec`); the pipeline graph
under `generated/assets/graphs/`; the bibliography at
`data/references/references.bib`. Committed `data/intermediate/sample_*` files
show representative shapes without running anything.

The generated document is primarily Hebrew (RTL), using English only for
technical terms (Agent, Task, Crew, Harness, validation), and includes an
explicit Hebrew↔English BiDi block to demonstrate the RTL↔LTR transition.

## 6. Visual Evidence

Screenshots of representative PDF pages are committed under `assets/screenshots/`.
The LaTeX pipeline has landed: `main.tex` is rendered on every run, and
`--build-pdf` compiles the final PDF end-to-end. The compiled,
19-page `final.pdf` is committed (a snapshot at the repo root, plus
`generated/pdf/final.pdf`) and serves as the primary visual deliverable.
Reproducing it from scratch requires a free TeX toolchain (lualatex + biber)
and the Hebrew font David CLM (culmus).
