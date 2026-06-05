# Extensibility & Extension Model

This note documents how BookGen is extended: where new behavior plugs in, the
lifecycle stages an extension can attach to, the single middleware choke point
for external calls, and the contracts each building block exposes. It is honest
about what exists today (dependency-injected building blocks behind one facade)
and what does *not* yet exist (a formal plugin registry), pointing at the exact
seam where the latter would go.

It satisfies the documentation tasks T538–T543 (extension points, lifecycle
hooks, stage middleware, extension interfaces, separation-of-concerns review,
and debuggability/reuse review).

## 1. The extension model in one paragraph

BookGen is **not** a plugin platform; it is a set of small, single-responsibility
building blocks wired together at exactly one place — the `BookGenSDK` facade
(`src/bookgen/sdk/sdk.py`). Every block has an explicit input/output contract and
takes its dependencies by injection (`root_dir`, `*_path`, `templates_dir`,
config objects), so a block can be swapped, wrapped, or added by editing that one
wiring site rather than reaching into callers. "Extending" the project therefore
means: implement a block that honors a contract, then wire it into the SDK (or
into the crew/asset/build sub-assemblies the SDK calls). There is no runtime
discovery, no entry-point scan, and no registry — extension is by composition and
dependency injection, reviewed and tested like any other code.

## 2. Lifecycle stages (T539)

The pipeline is a fixed, sequential, synchronous chain — this is deliberate for
determinism and reproducibility (see `docs/PARALLELISM.md`). `BookGenSDK`
exposes the lifecycle as four ordered, individually callable methods, and
`generate_book()` runs them in order:

```
run_crew()  ->  generate_assets()  ->  build_document()  ->  (compile)
```

| Stage | SDK method | Input contract | Output contract |
| :--- | :--- | :--- | :--- |
| Authoring (crew) | `run_crew(dry_run=True)` | config `root_dir`; dry-run refreshes committed sample artifacts, real run needs `OPENAI_API_KEY` | intermediate artifacts under `generated/intermediate/` (`book_plan.json`, `latex_spec.json`, …) + `CrewRunResult` |
| Asset generation | `generate_assets()` | — | image + graph PNGs under `generated/assets/`; returns `{"graph": path, "image": path}` |
| Document build | `build_document(compile_after=False)` | `book_plan.json` + `latex_spec.json` + metadata | rendered `generated/latex/main.tex`; summary dict |
| Compilation | `build_document(compile_after=True)` | `main.tex` + `latex_config` | `generated/pdf/final.pdf` (degrades gracefully with no TeX toolchain) |

These method boundaries **are** the lifecycle hooks. Because each stage reads its
inputs from disk and writes its outputs to disk under a `root_dir` you control,
you can:

- run a single stage in isolation (e.g. re-render the document from existing
  intermediate artifacts without re-running the crew);
- insert a "hook" by composing around an SDK method — call the stage, then run
  your own step on its declared output, then call the next stage. There is no
  callback/event bus; composition at the SDK boundary is the supported hook
  mechanism, and it keeps the pipeline order explicit and testable.

The natural place to formalize pre/post hooks (if ever wanted) is inside
`BookGenSDK.generate_book()`, which is the only code that owns the full stage
ordering. See §6 for the registry/hook seam.

## 3. Middleware: the gatekeeper choke point (T540)

The pipeline has exactly one middleware-style interception point, and it sits
where it matters most — **every external (model/provider) call**. The
`ApiGatekeeper` (`src/bookgen/shared/gatekeeper.py`) wraps a callable with
rate-limiting (per-minute window), transient-failure retries, backpressure
(`BackpressureError` on queue depth), and metrics (`get_queue_status()`):

```python
gatekeeper.execute(crew.kickoff, inputs={"topic": ...})
```

Real crew execution in `run_crew()` routes `crew.kickoff` through
`gatekeeper.execute(...)`, so cross-cutting concerns (throttling, retries,
observability) are added in one place rather than scattered across call sites.
`time_fn`/`sleep_fn` are injectable, so the middleware is deterministically
testable without a real provider or real wall-clock waits.

To add provider-call middleware (logging, caching, a circuit breaker, a budget
guard), wrap or extend `ApiGatekeeper.execute` — it is the single seam through
which all outbound calls must pass. The deterministic stages
(asset generation, rendering, compilation) intentionally do **no** provider I/O
and therefore do not pass through the gatekeeper; their "middleware" is plain
function composition at the SDK boundary.

## 4. Where a new extension plugs in (T538, T541)

Each block below has a stable, documented contract (mirrored in
`docs/PARALLELISM.md` §2). To extend, implement the contract and wire it in. The
extension interfaces are ordinary typed Python signatures and Pydantic schemas —
"clear interfaces" here means explicit inputs/outputs and dependency injection,
not abstract base classes.

### 4.1 A new asset generator (image / graph / table / formula)

- **Contract:** a function `f(output_path: Path | str = ...) -> Path` that writes
  one deterministic file and returns its path — mirroring
  `harness/assets.py::generate_image_asset` and
  `harness/graph_generator.py::generate_agent_pipeline_graph`.
- **Declare it:** add an `AssetSpec` to `REQUIRED_ASSETS` in `harness/assets.py`
  (`asset_id`, `kind`, `source`, `output_path`, `caption`).
- **Wire it:** call it from `BookGenSDK.generate_assets()` (the single asset
  assembly point), and reference it from `latex_spec.json` so the renderer emits
  it.
- **Thread-safety note:** any matplotlib-based generator must import `plt` from
  `harness/_mpl.py` (forces the headless Agg backend); never import `pyplot`
  directly. See `docs/PARALLELISM.md`.

### 4.2 A new validator / quality gate

- **Contract:** a function taking artifact paths and returning a
  `ValidationReport` of `ValidationCheck`s — exactly like
  `document/validators.py::validate_required_document_features`. Use the
  `_report_from_checks` pattern so a failed check becomes an error entry.
- **Wire it:** call it from `validate_project` (the validator aggregation point),
  appending its checks to the combined report. Keep checks pure and
  path-injected (`root_dir`/`*_path`) so they unit-test against a `tmp_path`.

### 4.3 A new agent and/or task

- **Agent contract:** a factory like `orchestration/agents.py::create_*_agent`
  returning a real `crewai.Agent` (or the `DryRunAgent` fallback when CrewAI is
  absent). Register it in `create_all_agents` under a responsibility key.
- **Task contract:** a factory like `orchestration/tasks.py::create_*_task`
  returning a `crewai.Task` (or `DryRunTask`) with `description`,
  `expected_output`, `agent`, and an explicit `context=[...]` list naming the
  upstream tasks it depends on. Register it in `create_all_tasks`, preserving the
  sequential `context` chain.
- **Skills:** attach knowledge packs by adding an entry to `SKILL_ASSIGNMENTS` in
  `orchestration/skills.py` (agent key → skill directory names under `skills/`);
  `assigned_skill_paths` injects only the packs that actually exist on disk.
- **Dry-run parity:** add the new artifact to the dry-run synthesizer and the
  shared artifact map (`shared/constants.py` / `orchestration/dry_run.py`) so the
  no-API path and the validators stay aligned and never drift.

### 4.4 An alternative renderer or templates

- **Contract:** a function with the `renderer.py::render_main_tex` shape —
  `(latex_spec, book_plan, metadata, output_dir=..., templates_dir=...,
  references_bib=...) -> Path`. All agent-authored text must be passed through
  `latex/escaping.py::escape_latex` first (injection-safety is part of the
  contract).
- **Wire it:** `build.py::build_document` calls the renderer; swap the import or
  pass a different `templates_dir`. The Jinja environment already uses
  `\VAR{}`/`\BLOCK{}` delimiters so templates can be replaced without touching
  Python.

### 4.5 An alternative compiler / output target

- **Contract:** a function with the `latex/compiler.py::compile_pdf` shape that
  returns a result carrying `success`, `message`, and `pdf_path`. `build_document`
  reads `engine`/`bibliography_backend`/`passes`/`output_pdf` from
  `latex_config` (the serialized `latex` config block), so a new engine is a
  config change plus a compatible compiler function.

## 5. Separation of concerns (T542)

The codebase enforces a strict split between **deciding** and **doing**:

- **Agents reason; the harness acts.** CrewAI agents/tasks
  (`orchestration/`) produce intent as JSON artifacts. Deterministic Python
  blocks (`harness/`, `latex/`, `document/`) consume those artifacts and produce
  reproducible output. No block both reasons *and* renders.
- **One block, one responsibility.** Config loading, schemas, validation,
  citation management, graph generation, escaping, rendering, and compilation are
  separate modules, each with a single input→output contract (table in
  `docs/PARALLELISM.md` §2).
- **One assembly point.** `BookGenSDK` is the only place blocks are wired
  together. `main.py` holds no business logic — it parses argv and delegates to
  the SDK. Swapping a block touches the one wiring site, not every caller.
- **One outbound choke point.** All provider I/O passes through `ApiGatekeeper`;
  cross-cutting policy lives there, not in the agents.
- **Layering direction.** `sdk → orchestration/latex/harness/document → shared`.
  Lower layers never import the SDK; the facade depends inward only.

## 6. Debuggability & reuse (T543)

**Debuggability.**

- **Stages are independently invokable.** Each SDK method is a self-contained
  step reading inputs from and writing outputs to disk, so you can reproduce or
  bisect a failure stage-by-stage without running the whole pipeline.
- **Deterministic by default.** The default `--dry-run` path uses committed
  sample artifacts and does no network I/O, so a failure is reproducible from the
  same inputs every time.
- **Injectable clock and sleep.** `ApiGatekeeper` takes `time_fn`/`sleep_fn`, so
  rate-limit and retry behavior is testable and traceable without real waits.
- **Structured logging & metrics.** `shared/logging.py` configures logging; the
  gatekeeper logs retries/failures and exposes `get_queue_status()` for queue
  depth and call counts.
- **Typed contracts fail fast.** Pydantic schemas (`document/schemas.py`) reject
  malformed artifacts at the stage boundary with a precise error rather than
  failing deep inside the renderer.

**Reuse.**

- **No hidden global state** (the one exception, matplotlib, is contained in
  `harness/_mpl.py`), so each block is unit-tested alone and can be lifted into
  another pipeline.
- **Dependency injection everywhere** (`root_dir`/`*_path`/`templates_dir`/config
  objects) means a block is rebound to new locations without code changes —
  tests inject `tmp_path`; a different host injects different roots.
- **The SDK is the reusable surface.** External consumers (CLI, a service, tests)
  call `BookGenSDK`, never internal modules, so the internals can be refactored
  without breaking consumers.

## 7. What does not exist yet: the registry seam

There is **no formal plugin registry, entry-point discovery, or hook/event bus**
today, and that is intentional for a deterministic, gradeable pipeline. Extension
is by composition + dependency injection, reviewed as normal code. If a future
version needs dynamic, third-party extensions, the seams are already isolated:

- **A plugin/extension registry** would live alongside `BookGenSDK` in
  `src/bookgen/sdk/`, registering implementations of the four contracts in §4
  (asset generator, validator, agent/task, renderer/compiler) and having the SDK
  resolve them instead of importing concrete functions directly. The SDK methods
  already centralize each assembly point, so only the wiring inside the SDK would
  change.
- **Lifecycle pre/post hooks** would be added inside
  `BookGenSDK.generate_book()`, the single owner of stage ordering — a list of
  callables invoked around each `run_crew`/`generate_assets`/`build_document`
  call. No stage internals would need to change.
- **Provider-call middleware** is already pluggable today by wrapping or
  subclassing `ApiGatekeeper.execute`; a middleware chain (list of wrappers)
  would slot in there without touching agents.

Keeping these as documented seams rather than speculative machinery preserves the
project's core properties — determinism, reproducibility, and a single, auditable
assembly point — while making the path to a real plugin system explicit.
