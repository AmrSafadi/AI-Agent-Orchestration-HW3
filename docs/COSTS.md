# Cost & Pricing Analysis

Required by the engineering standards (costs & pricing) and submission guideline
11. This documents what the system costs to run and how cost scales with usage.

## 1. Cost model — two very different paths

| Path | Command | LLM API cost | Compute |
|---|---|---|---|
| Dry-run (default) | `python -m bookgen.main` / `--dry-run` | **$0** — never calls a provider | Negligible local Python |
| Real crew | `python -m bookgen.main --run-crew` | **Paid** — 5 sequential agents call the LLM | Local |
| LaTeX compile (planned) | renderer + compiler | **$0** — fully local LuaLaTeX/biber | CPU only |

Only the real crew path spends money. All deterministic harness work (citations,
graph, validation, rendering, PDF compilation) is free local compute.

## 2. Where tokens are spent

The real run is a 5-task sequential pipeline; each task sends its prompt plus the
accumulated context and receives output:

| Stage | Input (context) | Output |
|---|---|---|
| Planner | topic + requirements | book plan |
| Research | + book plan | research pack |
| Writer | + plan + research | full manuscript (largest output) |
| Reviewer | + manuscript | review report + fixes |
| LaTeX | + reviewed manuscript | latex spec |

Context grows down the chain, so the **Writer and Reviewer stages dominate**
token usage.

## 3. Illustrative per-run estimate (default model)

Default model is `gpt-4o-mini` (`config/models.json`). Prices below are
**illustrative — verify current provider pricing before relying on them.**

| | Tokens (est.) | $/1M (illustrative) | Cost |
|---|---|---|---|
| Input (all stages, growing context) | ~40,000 | $0.15 | ~$0.006 |
| Output (manuscript-heavy) | ~25,000 | $0.60 | ~$0.015 |
| **Per full run** | | | **~$0.02** |

A ~15-page document on `gpt-4o-mini` is on the order of **a few cents per run**.

## 4. How cost scales with usage

- **Per run:** `cost ≈ input_tokens × input_price + output_tokens × output_price`.
- **Document length:** doubling target pages roughly doubles Writer output tokens.
- **Chapters:** more chapters → more Writer/Reviewer context and output (≈ linear).
- **Retries / revision loops:** each extra pass re-sends context (super-linear).
- **Model choice:** the single biggest lever (see §5).
- **Number of generations:** linear — N runs ≈ N × per-run cost.

## 5. Model cost comparison (illustrative)

| Model tier | Relative cost/run | Use when |
|---|---|---|
| `gpt-4o-mini` (default) | 1× (~$0.02) | Drafts, development, most homework runs |
| Mid frontier | ~10–20× | Higher-quality prose |
| Top frontier | ~20–40× (~$0.50–$1.00) | Final polish only |

## 6. Budgeting & controls

- `config/budgets.json` holds budget caps (currently placeholders).
- `shared/gatekeeper.py` is implemented: `ApiGatekeeper` is the single choke point
  for provider calls. It enforces a per-minute 60s sliding-window rate limit, retries
  via `max_retries`/`retry_after_seconds`, and applies backpressure by raising
  `BackpressureError` once `max_queue_depth` is exceeded; `get_queue_status()` exposes
  queue/rate state for monitoring.
- The gatekeeper does **not** track per-call token usage. Actual token usage for a
  real run comes from `result.token_usage` returned by `crew.kickoff()`.

## 7. Optimization strategies

- Develop and test on the **free dry-run path**; spend only on final real runs.
- Use `gpt-4o-mini` for drafts; reserve frontier models for a final pass.
- Keep prompts/backstories tight; avoid re-sending unneeded context.
- Persist intermediate artifacts so a re-run can skip completed stages.
- Avoid unnecessary revision loops; batch where possible.
