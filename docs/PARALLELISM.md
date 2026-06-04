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
