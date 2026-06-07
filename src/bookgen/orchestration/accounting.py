"""Token and budget accounting helpers for opt-in real crew runs."""

from __future__ import annotations

from typing import Any

from bookgen.shared.config import BudgetsConfig, ModelPrice

# Rough chars-per-token ratio for offline cost forecasting (no tokenizer needed).
_CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimate token count from text length (~4 chars/token) for forecasting."""
    return max(1, len(text) // _CHARS_PER_TOKEN)


def estimate_cost_usd(input_tokens: int, output_tokens: int, price: ModelPrice) -> float:
    """Estimate USD cost from token counts and per-million-token prices."""
    return (
        input_tokens / 1_000_000 * price.input_per_1m
        + output_tokens / 1_000_000 * price.output_per_1m
    )


def extract_token_usage(result: Any) -> dict[str, int | float]:
    """Extract common token/cost fields from CrewAI result objects."""
    usage: dict[str, int | float] = {}
    for candidate in _usage_candidates(result):
        plain = _to_plain(candidate)
        if isinstance(plain, dict):
            _collect_numbers(plain, usage)
    return usage


def budget_alerts(usage: dict[str, int | float], budgets: BudgetsConfig) -> list[str]:
    """Return config-driven budget warnings for token and USD caps."""
    alerts: list[str] = []
    total_tokens = _total_tokens(usage)
    warn_tokens = budgets.max_total_tokens * budgets.warn_at_percent / 100
    if total_tokens and total_tokens >= warn_tokens:
        alerts.append(
            f"token usage {int(total_tokens)} reached {budgets.warn_at_percent}% "
            f"of the configured {budgets.max_total_tokens} token budget"
        )
    if total_tokens and total_tokens > budgets.max_total_tokens:
        alerts.append(f"token usage {int(total_tokens)} exceeded the configured token budget")

    total_usd = _first_present(usage, ("total_usd", "total_cost_usd", "cost_usd"))
    if total_usd is not None and total_usd > budgets.max_total_usd:
        alerts.append(
            f"run cost ${total_usd:.4f} exceeded the configured ${budgets.max_total_usd:.2f} budget"
        )
    return alerts


def _usage_candidates(result: Any) -> list[Any]:
    """Return the result plus any nested usage objects it might expose."""
    candidates = [result]
    candidates.extend(
        getattr(result, name, None) for name in ("token_usage", "usage_metrics", "usage")
    )
    return [candidate for candidate in candidates if candidate is not None]


def _to_plain(value: Any) -> Any:
    """Coerce a usage object into a plain dict/scalar for inspection."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    return vars(value) if hasattr(value, "__dict__") else value


def _collect_numbers(
    source: dict[str, Any], usage: dict[str, int | float], prefix: str = ""
) -> None:
    """Recursively collect token/cost numeric fields into ``usage`` (dotted keys)."""
    for key, value in source.items():
        full_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            _collect_numbers(value, usage, full_key)
        elif isinstance(value, (int, float)) and (
            "token" in full_key.lower() or "cost" in full_key.lower()
        ):
            usage[full_key] = value


def _total_tokens(usage: dict[str, int | float]) -> float:
    """Return total tokens, preferring an explicit total over summed *_tokens."""
    direct = _first_present(
        usage, ("total_tokens", "token_usage.total_tokens", "usage.total_tokens")
    )
    if direct is not None:
        return float(direct)
    return float(sum(value for key, value in usage.items() if key.endswith("_tokens")))


def _first_present(usage: dict[str, int | float], keys: tuple[str, ...]) -> float | None:
    """Return the first numeric value among ``keys`` present in ``usage``."""
    for key in keys:
        value = usage.get(key)
        if isinstance(value, int | float):
            return float(value)
    return None
