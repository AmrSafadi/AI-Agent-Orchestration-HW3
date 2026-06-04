# Usability, Error Handling & Accessibility

This note documents how BookGen behaves at the edges: the boundary conditions of
each component and how each is handled (T517), accessibility considerations for
the command-line interface (T530), and the typical journeys a user takes through
the tool (T531).

The governing principle is **fail clearly or degrade gracefully**. Inputs that
make a correct run impossible (missing config, malformed schema, no API key for a
real run) raise a clear, single-sentence error and the CLI returns a non-zero
exit code. Inputs that merely reduce completeness (a missing optional asset, an
absent TeX toolchain) degrade gracefully: the pipeline still produces what it
can and reports what it could not do.

## 1. Boundary conditions per component (T517)

Each building block has an explicit input contract (see
[PARALLELISM.md §2](PARALLELISM.md)). The table below lists the boundary inputs
per component and the handling strategy — a **clear error** (raised exception,
caught at the CLI, exit code 1) or **graceful degradation** (the run continues
with a reduced or empty result, reported to the user or in a report).

| Component | Boundary condition | Handling | Mechanism |
| :--- | :--- | :--- | :--- |
| `shared/config.py` | Required config file missing | **Clear error** | `load_json_file` raises `FileNotFoundError("Missing config file: …")`; CLI catches it and returns 1. |
| `shared/config.py` | Config file is valid JSON but not an object (e.g. a list) | **Clear error** | `load_json_file` raises `ValueError("Config file must contain a JSON object: …")`. |
| `shared/config.py` | `version` field does not match `EXPECTED_CONFIG_VERSION` ("1.00") | **Clear error** | `_validate_config_versions` raises `ValueError` naming every mismatched file and the expected version. |
| `shared/config.py` | Required agent missing from `workflow.agents` / `models.agent_models` | **Clear error** | Pydantic `field_validator` raises `ValueError("missing required agents: …")`. |
| `document/schemas.py` | Empty required string field (title, topic, author, etc.) | **Clear error** | `Field(min_length=1)` raises `pydantic.ValidationError` at parse time. |
| `document/schemas.py` | Empty required collection (no chapters, no sections, no checklist) | **Clear error** | `Field(min_length=1)` on the list rejects empty input. |
| `document/schemas.py` | Out-of-range numeric field (e.g. `estimated_pages <= 0`, `temperature` outside 0–2, `warn_at_percent` outside 1–100) | **Clear error** | Pydantic `gt`/`ge`/`le` constraints raise `ValidationError`. |
| `document/schemas.py` | Unsupported LaTeX engine or asset kind | **Clear error** | `LatexSpec.engine` validator rejects anything but `lualatex/xelatex/pdflatex`; `LatexAsset.kind` is a `Literal["image","graph","table","formula"]`. |
| `document/validators.py` | Required intermediate artifact file does not exist | **Graceful (report, no raise)** | `validate_required_artifacts` records a failing `ValidationCheck` and returns a `ValidationReport` with `passed=False` and the missing path listed in `errors`. |
| `document/validators.py` | Plan/spec/manuscript not yet generated | **Graceful** | `validate_project` returns the artifact-only report instead of attempting feature checks against files that do not exist. |
| `document/validators.py` | A required document feature is absent (no cover/TOC placement, no citation marker, missing image/graph/table/formula asset, no mixed Hebrew–English text) | **Graceful (report, no raise)** | Each feature is a `ValidationCheck`; failures collect into `ValidationReport.errors` with an explanatory message rather than aborting. |
| `latex/escaping.py` | Untrusted text containing LaTeX control characters (`\\ & % $ # _ { } ~ ^`) | **Graceful (sanitized)** | Single-pass regex substitution makes agent-authored text injection-safe before templating; no input is rejected. |
| `latex/renderer.py` | LaTeX spec declares no asset of a requested kind | **Graceful** | `_asset` returns empty path/caption strings; the template omits that figure rather than failing. |
| `latex/renderer.py` | `references_bib` not provided or missing on disk | **Graceful** | The bibliography is copied only when the file exists; rendering of `main.tex` still completes. |
| `latex/compiler.py` | No TeX toolchain (engine or `biber` not on `PATH`) | **Graceful degradation** | `toolchain_available` returns `False`; `compile_pdf` writes the reason to `build.log` and returns `CompileResult(success=False, pdf_path=None)` without raising. The render step has already produced `main.tex`. |
| `latex/compiler.py` | Compilation runs but produces no PDF (e.g. undefined references, font missing) | **Graceful** | Each pass runs with `-interaction=nonstopmode`; all stdout/stderr is captured to `build.log`; `success` is `False` with the message "Compilation finished without a PDF; see build.log." Cross-reference/citation warnings are resolved by the multi-pass sequence (engine → biber → engine → engine). |
| `orchestration/crew.py` | `--run-crew` requested but CrewAI not installed | **Clear error** | Raises `RuntimeError("CrewAI is not installed; real crew execution is unavailable.")`. |
| `orchestration/crew.py` | `--run-crew` requested but `OPENAI_API_KEY` unset | **Clear error** | Raises `RuntimeError("OPENAI_API_KEY is required for real CrewAI execution.")`; CLI catches it and returns 1. |
| `shared/gatekeeper.py` | Deferred provider calls exceed `max_queue_depth` | **Clear error** | `ApiGatekeeper` raises `BackpressureError`; transient call failures are retried up to `max_retries` before re-raising. |

All exceptions raised on the default (dry-run) path are `FileNotFoundError`,
`ValueError`, or `pydantic.ValidationError` from configuration, plus `RuntimeError`
from the pipeline — exactly the set the CLI catches in `main.py`. Anything else
would be a defect rather than an expected boundary.

## 2. Accessibility considerations for the CLI (T530)

BookGen is a command-line tool with no graphical interface, so accessibility is
about predictable, assistive-technology-friendly terminal behavior.

- **Plain-text output only.** Status is printed as ordinary lines (config loaded,
  project title, topic, output directory, execution mode, completion message).
  There are no spinners, cursor-movement escape codes, progress bars, or redraws,
  so the output is fully consumable by screen readers and by log capture.
- **No color-only signals.** Meaning is never conveyed by color or styling alone.
  Success and failure are stated in words ("Dry-run completed", "PDF compiled",
  "Compilation finished without a PDF; see build.log") and reflected in the exit
  code, so the tool is usable with monochrome terminals and by color-blind users.
- **Deterministic, documented exit codes.** `0` means success; `1` means a
  configuration or pipeline error that was reported on stderr via the logger.
  Errors go through `configure_logging`, keeping diagnostics separate from the
  normal stdout status lines (clean stdout/stderr separation for scripting and
  assistive tooling).
- **UTF-8 and RTL-safe I/O.** All file reads and writes pass
  `encoding="utf-8"` explicitly, and the compiler captures subprocess output with
  `errors="replace"` so a non-UTF-8 byte in a TeX log never crashes the run. The
  generated document is Hebrew-primary (RTL) with English only for technical
  terms; bidirectional content is handled inside the document via the LaTeX BiDi
  setup, so console output stays plain ASCII status text and never depends on the
  terminal's RTL shaping.
- **Self-describing interface.** Every flag carries `argparse` help text, and
  `--help` lists the modes; the mutually exclusive `--dry-run` / `--run-crew`
  group prevents contradictory invocations. The safe mode is the default, so a
  user who runs the tool with no arguments cannot accidentally trigger paid API
  calls.
- **No interactive prompts.** The CLI never blocks on input, which keeps it
  usable from scripts, CI, and non-interactive assistive environments.

## 3. Typical user journeys (T531)

### Journey A — First-time dry-run (the safe default)

A new user wants to see the tool work without any setup, cost, or network.

1. Runs `python -m bookgen.main` (or `python -m bookgen.main --dry-run`; the two
   are equivalent because dry-run is the default).
2. The SDK loads and validates configuration. If a config file is missing or a
   version is wrong, the user gets a single clear error line and exit code 1
   (see §1) — nothing partial is produced.
3. On success the CLI prints the loaded project title, topic, output directory,
   and "Execution mode: DRY-RUN (default)."
4. The pipeline reads the committed sample artifacts, synthesizes the
   intermediate artifacts, generates assets, and renders `main.tex` — all
   locally, with no API call.
5. The run ends with "Rendered main.tex (LaTeX compilation not requested)." and
   exit code 0. The user can open `generated/latex/main.tex` and the artifacts
   under `generated/intermediate/`.

This journey never needs an API key or a TeX toolchain; it is the recommended
first experience and the path exercised by the test suite.

### Journey B — Render and build the PDF

A user wants the finished, compiled document.

1. Runs `python -m bookgen.main --build-pdf` (still dry-run; `--build-pdf` is an
   add-on, not a mode).
2. Steps 2–4 of Journey A run identically, producing `main.tex`.
3. `compile_pdf` checks for the toolchain:
   - **With** `lualatex` + `biber` on `PATH`: it runs the multi-pass sequence,
     writes `build.log`, and on success reports "PDF compiled." with the PDF
     path. (Verified end-to-end as an 18-page `final.pdf`.)
   - **Without** the toolchain: it degrades gracefully — writes the reason to
     `build.log`, reports that compilation was skipped, and still exits 0 because
     `main.tex` was rendered successfully. The user is told exactly what was
     missing and where to look.

The user is never left with a half-written PDF and a cryptic crash; the worst
case is a clearly explained "no PDF, here's why."

### Journey C — Real run with an API key

An advanced user wants a genuine CrewAI execution against a model provider.

1. Sets `OPENAI_API_KEY` in the environment and runs
   `python -m bookgen.main --run-crew`.
2. If CrewAI is not installed or the key is unset, the pipeline raises a clear
   `RuntimeError` (see §1), the CLI logs it, and returns exit code 1 — no
   provider call is attempted.
3. With the key present, every provider call is routed through the single
   `ApiGatekeeper`, which enforces the configured per-minute rate limit, retries
   transient failures up to `max_retries`, and raises `BackpressureError` if the
   deferred-call queue exceeds `max_queue_depth`.
4. After the crew completes, asset generation and document rendering proceed
   exactly as in the dry-run path, optionally followed by `--build-pdf`.

Because `--dry-run` and `--run-crew` are mutually exclusive and dry-run is the
default, a user must opt in explicitly and deliberately before any paid,
networked work can occur.

## See also

- [USAGE.md](USAGE.md) — commands, modes, and a sample session.
- [PARALLELISM.md](PARALLELISM.md) — per-component input/output contracts and the
  deliberate single-threaded, deterministic design.
