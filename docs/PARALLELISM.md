# Parallelism, Thread-Safety & Modular Building Blocks

This note covers two design dimensions the submission guidelines call out:
parallelism / thread-safety (§15) and modular building blocks (§16). It
describes the *current* deterministic design and the *safe* path to concurrency
if the project is extended.

## 1. Parallelism & thread-safety (§15)

### Stage classification

| Stage | Bound | Notes |
| :--- | :--- | :--- |
| Real CrewAI provider calls (`--run-crew`) | **I/O-bound** | Network round-trips to the model provider; routed through `shared/gatekeeper.py`. |
| Graph / image generation | **CPU-bound** | Matplotlib rendering (`harness/graph_generator.py`, `assets.py`). |
| LaTeX compilation (`--build-pdf`) | **CPU-bound** | External `lualatex`/`biber` processes (`latex/compiler.py`). |
| Config load, schema validation, citation extraction, rendering | CPU-light | Pure Python over small artifacts. |

### Why the current design is single-threaded and synchronous

- **Determinism first.** The harness must be reproducible for grading: the same
  inputs must yield the same `main.tex`. A fixed, serial order removes
  scheduling-dependent variation.
- **The pipeline is inherently sequential.** Each stage consumes the previous
  stage's artifact (`book_plan → research_pack → manuscript → review_report →
  latex_spec → main.tex`), so `Process.sequential` is the correct CrewAI process;
  there is no independent work to overlap on the critical path.
- **The default path does no I/O fan-out.** Dry-run reads committed samples and
  renders locally, so concurrency would add risk without benefit.

### The matplotlib global-state pitfall (already mitigated)

`matplotlib.pyplot` keeps process-global state and its default GUI backends are
not thread-safe (mixing them with worker threads raises `_tkinter.TclError`).
We import `matplotlib` through `harness/_mpl.py`, which forces the headless
**Agg** backend *before* `pyplot` is imported. If figure generation is ever
parallelized, render in **separate processes** (not threads), or serialize
figure calls behind a lock.

### Safe path to concurrency

If a future version fans out (e.g. researching many sources, or batch-rendering
assets):

- **I/O-bound work (provider calls):** a thread pool is appropriate. Keep
  `ApiGatekeeper` as the single choke point — it already enforces a per-minute
  rate-limit window and `BackpressureError` on queue depth, which is exactly the
  shared guard concurrent callers need.
- **CPU-bound work (matplotlib / LaTeX):** use a process pool to sidestep the GIL
  and matplotlib's global state.
- **Data transfer:** hand work between stages with `queue.Queue` (thread-safe);
  protect any shared counter/cache with a `threading.Lock`.
- **Deadlock/race avoidance:** acquire locks in a fixed order, keep critical
  sections small, and never block inside a lock on another queue.

The three subsections below are the concrete recipe to follow **if** concurrency
is ever added. They are deliberately *not* implemented today: the pipeline is
single-threaded and synchronous by design (see "Why the current design is
single-threaded" above), so these are forward-looking contracts, not live code.

#### T546 — Use `queue.Queue` for safe data transfer

Hand artifacts between stages through a bounded `queue.Queue`, never via shared
mutable variables. `queue.Queue` is internally synchronized (it owns its own
lock and condition variables), so producers and consumers never corrupt the
buffer and no caller-level locking is required for the hand-off itself.

```python
import queue, threading

stage_q: "queue.Queue[Artifact]" = queue.Queue(maxsize=8)  # bound = backpressure

def producer(plan):                      # e.g. research stage
    for artifact in render_stage(plan):
        stage_q.put(artifact)            # blocks when full -> natural backpressure
    stage_q.put(_SENTINEL)               # signal "no more items"

def consumer():                          # e.g. manuscript stage
    while (item := stage_q.get()) is not _SENTINEL:
        handle(item)
        stage_q.task_done()
```

- One `Queue` per stage boundary mirrors the existing linear pipeline
  (`book_plan → research_pack → manuscript → review_report → latex_spec →
  main.tex`).
- A bounded queue (`maxsize`) gives free backpressure, complementing the
  `BackpressureError` the gatekeeper already raises on queue depth.
- Use a sentinel (or `queue.shutdown()` on 3.13+) to close the stream so the
  consumer exits cleanly rather than blocking forever on `get()`.

#### T547 — Protect shared state with locks

The only shared mutable state worth protecting is inside
`shared/gatekeeper.py`: the per-minute call counter, the rate-limit window
timestamps, and the in-flight/backpressure depth. Under concurrency these must
be read-modified-written atomically.

```python
class ApiGatekeeper:
    def __init__(self, ...):
        self._lock = threading.Lock()
        self._calls_this_window = 0

    def _record_call(self):
        with self._lock:                 # guard the counter
            self._calls_this_window += 1
            window_count = self._calls_this_window
        return window_count              # do work *outside* the lock
```

- Keep `ApiGatekeeper` the single choke point for provider calls so there is
  exactly one place that needs a lock, not one per call site.
- Guard counters/caches/windows; do **not** hold the lock across the actual
  network call or any `queue` operation (that is the deadlock trap below).
- Prefer `with self._lock:` over manual `acquire()/release()` so the lock is
  released even if the guarded block raises.

#### T548 — Avoid deadlocks and race conditions

- **Fixed lock ordering.** If more than one lock ever exists (e.g. gatekeeper
  counter lock + a cache lock), always acquire them in the same global order.
  Cyclic acquisition order is the classic deadlock.
- **No blocking inside a lock.** Never call `queue.get()`/`queue.put()`, sleep,
  or perform I/O while holding a `Lock`; copy out what you need, release, then
  block. This prevents the "holder waits on the queue while the producer waits
  on the lock" cycle.
- **Small critical sections.** Compute outside the lock, mutate inside it. The
  shorter the critical section, the lower the contention and the smaller the
  race window.
- **No check-then-act races.** Read-modify-write of shared counters must be a
  single locked region (see T547); never read a value, act, then write back
  across a lock boundary.
- **Determinism caveat.** Even a correct concurrent version is allowed to reorder
  *independent* work, so any output that must stay byte-identical for grading
  (the rendered `main.tex`) must remain on the serial path or be reassembled in a
  fixed, index-ordered sequence after the parallel fan-out completes.

### Performance benchmarking & spec sheet (T549, T550)

#### T549 — Benchmark stage latencies

Measure each stage's wall-clock time independently so the dominant cost is
visible before any concurrency is justified. A lightweight harness wraps each
stage call with `time.perf_counter()` (and `tracemalloc`/`resource` for memory)
and writes one row per stage:

```python
import time, tracemalloc

def timed(name, fn, *args):
    tracemalloc.start()
    t0 = time.perf_counter()
    out = fn(*args)
    dt = time.perf_counter() - t0
    _cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    record(name, wall_s=dt, peak_bytes=peak)
    return out
```

Benchmark the stage boundaries already named in the pipeline (config load,
schema validation, citation extraction, graph generation, rendering, and — for a
real run — provider calls and LaTeX compile). Run on the committed sample inputs
so the numbers are reproducible.

#### T550 — Performance spec sheet

The spec sheet reports three measurable dimensions per stage:

| Dimension | How measured | Notes |
| :--- | :--- | :--- |
| **Per-stage wall-clock latency** | `time.perf_counter()` around each stage | Dry-run stages (config, validation, citations, rendering) are CPU-light and **sub-second**. |
| **Peak memory** | `tracemalloc` (Python) / RSS for subprocesses | Matplotlib figure generation and `lualatex` dominate RSS; pure-Python stages are small. |
| **Token count (real run only)** | gatekeeper call accounting on `--run-crew` | Prompt + completion tokens per agent call; zero on the default dry-run (no API). |

Expected shape of the numbers:

- **Dry-run** (`--dry-run`, the default, no API): every stage is CPU-light and
  sub-second; total runtime is dominated by process start-up, not the stages.
- **`--build-pdf`:** the **LaTeX compile dominates** — multi-pass
  `lualatex`/`biber` is the single largest wall-clock and RSS contributor by a
  wide margin.
- **`--run-crew`** (real, off by default): network-bound provider latency
  dominates and is the only stage that consumes tokens; this is the I/O-bound
  case where the T546–T548 concurrency recipe would pay off.

Because the default path is dry-run, the spec sheet's headline finding is that
**no stage on the default critical path is a bottleneck** — concurrency is
unnecessary until real provider calls (`--run-crew`) or batch asset rendering are
introduced.

## 2. Modular building blocks (§16)

Each capability is an independent block: one module, one responsibility, an
explicit input/output/setup contract, and unit tests in isolation.

| Block | Input | Output | Responsibility |
| :--- | :--- | :--- | :--- |
| `shared/config.py` | `config/*.json` | typed `Config` | Load + version-validate configuration |
| `shared/constants.py` | — | immutable tuples/maps | Single source of truth for agents/artifacts/features |
| `shared/gatekeeper.py` | a callable + args | result | Rate-limit, retry, backpressure, monitoring |
| `document/schemas.py` | raw JSON | Pydantic models | Artifact contracts |
| `document/validators.py` | artifact paths | `ValidationReport` | Assert artifacts/features/files exist |
| `harness/citations.py` | source registry / text | `references.bib`, keys | Citation management |
| `harness/graph_generator.py` | pipeline spec | PNG | Python-generated graph |
| `latex/escaping.py` | untrusted text | LaTeX-safe text | Injection-safe escaping |
| `latex/renderer.py` | `book_plan` + `latex_spec` | `main.tex` | Deterministic templating |
| `latex/compiler.py` | `main.tex` | `final.pdf` | Multi-pass compile (graceful) |
| `sdk/sdk.py` | config | run result | Facade that assembles the blocks |

### Design properties

- **Single responsibility:** no block both decides *and* renders; the model
  reasons, the harness blocks act deterministically.
- **Dependency injection for testability:** `root_dir` and `*_path` parameters
  are threaded through `validators`, `renderer`, and `build`, so tests inject a
  `tmp_path` and assert outputs without touching the real tree.
- **Single assembly point:** `BookGenSDK` is the only place blocks are wired
  together; `main.py` holds no business logic. Swapping a block (e.g. a different
  graph generator) touches one wiring site.
- **Independent and reusable:** each block has no hidden global state (the one
  exception, matplotlib, is contained in `_mpl.py`), so blocks are unit-tested
  alone and could be reused in another pipeline.

### Template Method for varied-but-similar logic (T555)

Several places run the *same skeleton* with one varying step — the textbook case
for the Template Method pattern (a fixed algorithm with pluggable hook steps):

- **Agent / task factories (`orchestration/agents.py`, `orchestration/tasks.py`).**
  Every agent is built by the same recipe — read role/goal/backstory from
  `shared/constants.py`, attach the gatekeeper-routed LLM, set the shared flags —
  and only the per-agent fields differ. Likewise every task shares the
  description → expected-output → assigned-agent → upstream-context skeleton and
  varies only its content. The invariant skeleton lives in one builder; the
  per-agent / per-task data are the hook values, so adding an agent or task means
  supplying data, not duplicating control flow.
- **The renderer's snippet-materialization loop (`latex/renderer.py`).** Each
  chapter/section is materialized by the same sequence — select template, escape
  untrusted text via `latex/escaping.py`, substitute fields, append — and only
  the per-snippet template and payload vary. The loop is the template method; the
  per-snippet template selection is the overridable step.

Applying Template Method here keeps the shared control flow in exactly one place,
so a change to the skeleton (e.g. a new validation step before every task) is
made once rather than copied across every variant.

### Mixin discipline (T556)

Where small, orthogonal behaviours are composed onto a class, they must follow
strict mixin rules:

- **Single concern per mixin.** A mixin adds exactly one capability (e.g. timing,
  monitoring/accounting, or backpressure accounting around a call) and nothing
  else. It does not also own unrelated state or reach into the host's internals
  beyond the one collaborator it declares.
- **Independently testable.** Each mixin is exercised in isolation against a
  minimal host stub — no full pipeline, no real provider, no file tree — so its
  behaviour is verified on its own. This mirrors the dependency-injection rule
  above (`root_dir` / `*_path` parameters) that already lets every block be
  unit-tested alone.
- **Composable without coupling.** Mixins must not depend on one another's
  ordering or shared hidden state; combining two mixins yields the union of their
  (independent) behaviours with no interaction term. Anything that needs to
  coordinate state belongs in a real collaborator (e.g. `ApiGatekeeper`), not a
  mixin.
