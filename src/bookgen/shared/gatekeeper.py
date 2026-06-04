"""Centralized API gatekeeper: rate limiting, retries, queue status, monitoring.

Guideline 5 requires every external (LLM/provider) call to pass through one
gatekeeper. ``execute()`` runs a callable under the configured rate limit,
retries transient failures, and records metrics. Time and sleep are injectable
so the behavior is deterministically testable without a real provider.
"""

from __future__ import annotations

import logging
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from bookgen.shared.config import RateLimitsConfig

_WINDOW_SECONDS = 60.0


class BackpressureError(RuntimeError):
    """Raised when deferred calls exceed the configured maximum queue depth."""


@dataclass
class QueueStatus:
    """Snapshot of recent gatekeeper activity."""

    recent_calls: int
    total_calls: int
    max_per_minute: int


class ApiGatekeeper:
    """Single, monitored entry point for all external API calls."""

    def __init__(
        self,
        config: RateLimitsConfig,
        time_fn: Callable[[], float] = time.monotonic,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self._config = config
        self._time = time_fn
        self._sleep = sleep_fn
        self._calls: deque[float] = deque()
        self._total = 0
        self._logger = logging.getLogger("bookgen.gatekeeper")

    def execute(self, api_call: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Run ``api_call`` under the rate limit, retrying transient failures."""
        self._enforce_rate_limit()
        for attempt in range(self._config.max_retries + 1):
            try:
                self._record()
                return api_call(*args, **kwargs)
            except Exception as exc:
                if attempt >= self._config.max_retries:
                    self._logger.error("API call failed after %d attempts: %s", attempt + 1, exc)
                    raise
                self._logger.warning("API call failed (attempt %d); retrying: %s", attempt + 1, exc)
                self._sleep(self._config.retry_after_seconds)
        raise RuntimeError("unreachable")  # pragma: no cover

    def get_queue_status(self) -> QueueStatus:
        """Return a snapshot of recent and total activity."""
        self._prune()
        return QueueStatus(
            recent_calls=len(self._calls),
            total_calls=self._total,
            max_per_minute=self._config.requests_per_minute,
        )

    def _enforce_rate_limit(self) -> None:
        self._prune()
        if len(self._calls) >= self._config.requests_per_minute:
            if len(self._calls) - self._config.requests_per_minute >= self._config.max_queue_depth:
                raise BackpressureError("rate-limit queue exceeded its maximum depth")
            self._sleep(max(_WINDOW_SECONDS - (self._time() - self._calls[0]), 0.0))
            self._prune()

    def _record(self) -> None:
        self._calls.append(self._time())
        self._total += 1

    def _prune(self) -> None:
        now = self._time()
        while self._calls and now - self._calls[0] > _WINDOW_SECONDS:
            self._calls.popleft()
