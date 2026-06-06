# Cost & Pricing Analysis

Required by the engineering standards (costs & pricing) and submission guideline
11. This documents what the system costs to run and how cost scales with usage.

## 1. Cost Model -- Two Very Different Paths

| Path | Command | LLM API cost | Compute |
|---|---|---|---|
| Dry-run (default) | `python -m bookgen.main` / `--dry-run` | **$0** -- never calls a provider | Negligible local Python |
| Real crew | `python -m bookgen.main --run-crew` | **Paid** -- 5 sequential agents call the LLM | Local |
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

## 3. Illustrative Per-Run Estimate

Default model is `gpt-4o-mini` (`config/models.json`). Prices below are
illustrative; verify current provider pricing before relying on them.

| | Tokens (est.) | $/1M (illustrative) | Cost |
|---|---|---|---|
| Input (all stages, growing context) | ~40,000 | $0.15 | ~$0.006 |
| Output (manuscript-heavy) | ~25,000 | $0.60 | ~$0.015 |
| **Per full run** | | | **~$0.02** |

A ~15-page document on `gpt-4o-mini` is on the order of a few cents per run.

## 4. How Cost Scales

- Per run: `cost = input_tokens * input_price + output_tokens * output_price`.
- Document length: doubling target pages roughly doubles Writer output tokens.
- Chapters: more chapters produce more Writer/Reviewer context and output.
- Retries / revision loops: each extra pass re-sends context.
- Model choice: the single biggest lever.
- Number of generations: linear.

## 5. Model Cost Comparison

| Model tier | Relative cost/run | Use when |
|---|---|---|
| `gpt-4o-mini` (default) | 1x (~$0.02) | Drafts, development, most homework runs |
| Mid frontier | ~10-20x | Higher-quality prose |
| Top frontier | ~20-40x (~$0.50-$1.00) | Final polish only |

## 6. Budgeting & Controls

- `config/budgets.json` holds budget caps: `max_total_tokens`,
  `max_total_usd`, and `warn_at_percent`.
- `shared/gatekeeper.py` is implemented: `ApiGatekeeper` is the single choke
  point for provider calls. It enforces a 60-second sliding-window rate limit,
  retries via `max_retries` / `retry_after_seconds`, and applies backpressure by
  raising `BackpressureError` once `max_queue_depth` is exceeded.
- `orchestration/accounting.py` extracts token/cost fields exposed by CrewAI
  result objects (`token_usage`, `usage_metrics`, or `usage`).
- `orchestration/real_run.py` persists real-run task outputs, token usage, and
  budget alerts to `generated/intermediate/real_run_trace.json` and
  `generated/intermediate/real_run_summary.json`.
- Budget alerts are config-driven. A real run records warnings when total tokens
  cross `warn_at_percent` or exceed `max_total_tokens`; if CrewAI exposes a USD
  cost field, it is checked against `max_total_usd`.

## 7. Optimization Strategies

- Develop and test on the free dry-run path; spend only on final real runs.
- Use `gpt-4o-mini` for drafts; reserve frontier models for final polish.
- Keep prompts/backstories tight; avoid re-sending unneeded context.
- Persist intermediate artifacts so a re-run can inspect or resume work.
- Avoid unnecessary revision loops; batch feedback where possible.
