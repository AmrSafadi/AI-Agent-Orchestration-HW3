# Cost & Pricing Analysis

Required by the engineering standards (costs & pricing) and submission guideline
11. This documents what the system costs to run and how cost scales with usage.

## 1. Cost Model -- Two Very Different Paths

| Path | Command | LLM API cost | Compute |
|---|---|---|---|
| Dry-run (default) | `uv run --no-project --with pydantic --with matplotlib --with jinja2 python -m bookgen.main` / `--dry-run` | **$0** -- never calls a provider | Negligible local Python |
| Real crew | `uv run python -m bookgen.main --run-crew` | **Paid** -- 5 sequential agents call the LLM | Local |
| LaTeX compile | renderer + compiler | **$0** -- fully local LuaLaTeX/biber | CPU only |

Only the real crew path spends money. All deterministic harness work (citations,
graph, validation, rendering, PDF compilation) is free local compute.

## 2. Where Tokens Are Spent

The real run is a 5-task sequential pipeline; each task sends its prompt plus the
accumulated context and receives output:

| Stage | Input (context) | Output |
|---|---|---|
| Planner | topic + requirements | book plan |
| Research | + book plan | research pack |
| Writer | + plan + research | full manuscript (largest output) |
| Reviewer | + manuscript | review report + fixes |
| LaTeX | + reviewed manuscript | latex spec |

Context grows down the chain, so the Writer and Reviewer stages dominate token
usage.

## 3. Model Pricing (config-driven)

Prices come directly from the `pricing` block in `config/models.json`, so the
estimate below is **config-driven and code-backed** rather than illustrative.
Provider list prices change over time; update the config when they do and the
estimate follows automatically.

| Model | Input $/1M tokens | Output $/1M tokens |
|---|---|---|
| `gpt-4o-mini` (default) | $0.15 | $0.60 |
| `gpt-4o` | $2.50 | $10.00 |
| `claude-sonnet-4-6` | $3.00 | $15.00 |

## 4. Estimated Cost For A Typical ~15-Page Run

A ~15-page document is roughly ~40,000 input tokens (all stages, growing
context) and ~25,000 output tokens (manuscript-heavy). Applying the config
prices above:

| Model | Input cost | Output cost | **Per full run** |
|---|---|---|---|
| `gpt-4o-mini` | ~$0.006 | ~$0.015 | **~$0.02** |
| `gpt-4o` | ~$0.10 | ~$0.25 | **~$0.35** |
| `claude-sonnet-4-6` | ~$0.12 | ~$0.375 | **~$0.50** |

So a ~15-page document on the default `gpt-4o-mini` is on the order of a few
cents per run; frontier models are roughly $0.35-$0.50.

**Code-backed estimate.** `BookGenSDK.estimate_cost()` forecasts this on the
dry-run path (no API call): it sizes the manuscript with
`orchestration/accounting.py::estimate_tokens`, applies the
`config/models.json` price for the configured model via
`accounting.py::estimate_cost_usd`, and returns the projected input/output
tokens and USD. Because both the token sizing and the pricing are code + config,
the forecast tracks the actual configuration instead of a hand-written guess.

## 5. How Cost Scales

- Per run: `cost = input_tokens * input_price + output_tokens * output_price`.
- Document length: doubling target pages roughly doubles Writer output tokens.
- Chapters: more chapters produce more Writer/Reviewer context and output.
- Retries / revision loops: each extra pass re-sends context.
- Model choice: the single biggest lever.
- Number of generations: linear.

## 6. Model Cost Comparison

| Model | Relative cost/run | Use when |
|---|---|---|
| `gpt-4o-mini` (default) | 1x (~$0.02) | Drafts, development, most homework runs |
| `gpt-4o` | ~17x (~$0.35) | Higher-quality prose |
| `claude-sonnet-4-6` | ~25x (~$0.50) | Final polish only |

## 7. Budgeting & Controls

- `config/budgets.json` holds budget caps: `max_total_tokens`,
  `max_total_usd`, and `warn_at_percent`.
- `shared/gatekeeper.py` is implemented: `ApiGatekeeper` is the single choke
  point for provider calls. It is thread-safe and enforces per-minute **and**
  per-hour rate limits plus a `concurrent_max` cap, retries via `max_retries` /
  `retry_after_seconds`, and applies backpressure by raising `BackpressureError`
  once `max_queue_depth` is exceeded. The gatekeeper does **not** do token or
  budget accounting — that lives in `accounting.py` and `real_run.py` (below);
  the gatekeeper only handles rate-limiting, retries, and backpressure.
- `orchestration/accounting.py` extracts token/cost fields exposed by CrewAI
  result objects (`token_usage`, `usage_metrics`, or `usage`) and provides
  `estimate_tokens` / `estimate_cost_usd` for the config-driven forecast.
- `orchestration/real_run.py` persists real-run task outputs, token usage, and
  budget alerts to `generated/intermediate/real_run_trace.json` and
  `generated/intermediate/real_run_summary.json`.
- Budget alerts are config-driven. A real run records warnings when total tokens
  cross `warn_at_percent` or exceed `max_total_tokens`; if CrewAI exposes a USD
  cost field, it is checked against `max_total_usd`.

## 8. Optimization Strategies

- Develop and test on the free dry-run path; spend only on final real runs.
- Use `gpt-4o-mini` for drafts; reserve frontier models for final polish.
- Keep prompts/backstories tight; avoid re-sending unneeded context.
- Persist intermediate artifacts so a re-run can inspect or resume work.
- Avoid unnecessary revision loops; batch feedback where possible.
