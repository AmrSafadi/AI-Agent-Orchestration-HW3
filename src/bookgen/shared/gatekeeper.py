"""Centralized API gatekeeper: rate limiting, retries, queue status, monitoring.

Guideline 5 requires every external (LLM/provider) call to pass through one
gatekeeper. ``execute()`` runs a callable under the configured per-minute and
per-hour rate limits and a concurrency cap, retries transient failures, and
records metrics. Time and sleep are injectable so the behavior is
deterministically testable without a real provider.

Overflow model: when the per-minute (or per-hour) window is full the caller is
blocked until the window's oldest call ages out (synchronous backpressure). If
the backlog beyond the limit reaches ``max_queue_depth``, a ``BackpressureError``
is raised instead of queueing unboundedly. A ``threading.Lock`` guards the
sliding-window state and a semaphore enforces ``concurrent_max`` so the gatekeeper
is safe under multithreaded use (guideline 15.2).

Monitoring (guideline 5.1): every call is logged via the ``bookgen.gatekeeper``
logger, and a backpressure **alert** (``logger.warning``) is emitted before the
``BackpressureError`` is raised when the queue is full.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from bookgen.shared.config import RateLimitsConfig

_WINDOW_SECONDS = 60.0
_HOUR_SECONDS = 3600.0


class BackpressureError(RuntimeError):
    """Raised when deferred calls exceed the configured maximum queue depth."""


@dataclass
class QueueStatus:
    """Snapshot of recent gatekeeper activity."""

    recent_calls: int
    total_calls: int
    max_per_minute: int


class ApiGatekeeper:
    """Single, monitored, thread-safe entry point for all external API calls."""

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
        self._hour_calls: deque[float] = deque()
        self._total = 0
        self._lock = threading.Lock()
        self._slots = threading.Semaphore(config.concurrent_max)
        self._logger = logging.getLogger("bookgen.gatekeeper")

    def execute(self, api_call: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Run ``api_call`` under the rate/concurrency limits, retrying failures."""
        with self._slots:  # enforce concurrent_max
            self._enforce_rate_limit()
            for attempt in range(self._config.max_retries + 1):
                try:
                    self._record()
                    return api_call(*args, **kwargs)
                except Exception as exc:
                    if attempt >= self._config.max_retries:
                        self._logger.error(
                            "API call failed after %d attempts: %s", attempt + 1, exc
                        )
                        raise
                    self._logger.warning(
                        "API call failed (attempt %d); retrying: %s", attempt + 1, exc
                    )
                    self._sleep(self._config.retry_after_seconds)
        raise RuntimeError("unreachable")  # pragma: no cover

    def get_queue_status(self) -> QueueStatus:
        """Return a snapshot of recent and total activity."""
        with self._lock:
            self._prune()
            return QueueStatus(
                recent_calls=len(self._calls),
                total_calls=self._total,
                max_per_minute=self._config.requests_per_minute,
            )

    def _enforce_rate_limit(self) -> None:
        """Block until a per-minute/per-hour slot is free, or raise on overflow."""
        with self._lock:
            self._prune()
            minute_over = len(self._calls) >= self._config.requests_per_minute
            hour_over = len(self._hour_calls) >= self._config.requests_per_hour
            if (
                minute_over
                and len(self._calls) - self._config.requests_per_minute
                >= self._config.max_queue_depth
            ):
                self._logger.warning(
                    "backpressure alert: deferred calls exceeded max_queue_depth=%d",
                    self._config.max_queue_depth,
                )
                raise BackpressureError("rate-limit queue exceeded its maximum depth")
            wait = 0.0
            if minute_over and self._calls:
                wait = max(wait, _WINDOW_SECONDS - (self._time() - self._calls[0]))
            if hour_over and self._hour_calls:
                wait = max(wait, _HOUR_SECONDS - (self._time() - self._hour_calls[0]))
        if wait > 0:
            self._sleep(wait)
            with self._lock:
                self._prune()

    def _record(self) -> None:
        """Record one call timestamp in the minute and hour windows."""
        with self._lock:
            now = self._time()
            self._calls.append(now)
            self._hour_calls.append(now)
            self._total += 1
            self._logger.info("gatekeeper call #%d (recent=%d)", self._total, len(self._calls))

    def _prune(self) -> None:
        """Drop call timestamps that have aged out of their windows."""
        now = self._time()
        while self._calls and now - self._calls[0] > _WINDOW_SECONDS:
            self._calls.popleft()
        while self._hour_calls and now - self._hour_calls[0] > _HOUR_SECONDS:
            self._hour_calls.popleft()
