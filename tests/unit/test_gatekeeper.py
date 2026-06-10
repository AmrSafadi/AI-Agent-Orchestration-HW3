"""Tests for the centralized API gatekeeper (deterministic, no real API)."""

from __future__ import annotations

import pytest

from bookgen.shared.config import RateLimitsConfig
from bookgen.shared.gatekeeper import ApiGatekeeper, BackpressureError


def _config(**overrides: object) -> RateLimitsConfig:
    base = {
        "version": "1.00",
        "requests_per_minute": 2,
        "requests_per_hour": 100,
        "concurrent_max": 5,
        "retry_after_seconds": 0,
        "max_retries": 2,
        "max_queue_depth": 2,
    }
    base.update(overrides)
    return RateLimitsConfig(**base)


class _Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


def test_execute_runs_callable_and_counts() -> None:
    gatekeeper = ApiGatekeeper(_config(), time_fn=_Clock(), sleep_fn=lambda _: None)
    assert gatekeeper.execute(lambda value: value + 1, 41) == 42
    assert gatekeeper.get_queue_status().total_calls == 1


def test_rate_limit_triggers_wait() -> None:
    sleeps: list[float] = []
    gatekeeper = ApiGatekeeper(
        _config(requests_per_minute=2), time_fn=_Clock(), sleep_fn=sleeps.append
    )
    for _ in range(3):
        gatekeeper.execute(lambda: "ok")
    assert sleeps  # the 3rd call within the window forced a wait


def test_retry_then_success() -> None:
    sleeps: list[float] = []
    attempts = {"n": 0}

    def flaky() -> str:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ValueError("transient")
        return "done"

    gatekeeper = ApiGatekeeper(_config(max_retries=3), time_fn=_Clock(), sleep_fn=sleeps.append)
    assert gatekeeper.execute(flaky) == "done"
    assert len(sleeps) == 2


def test_retry_exhausted_raises() -> None:
    gatekeeper = ApiGatekeeper(_config(max_retries=1), time_fn=_Clock(), sleep_fn=lambda _: None)

    def always_fail() -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        gatekeeper.execute(always_fail)


def test_hourly_limit_triggers_wait() -> None:
    sleeps: list[float] = []
    gatekeeper = ApiGatekeeper(
        _config(requests_per_minute=100, requests_per_hour=2, max_queue_depth=100),
        time_fn=_Clock(),
        sleep_fn=sleeps.append,
    )
    for _ in range(3):
        gatekeeper.execute(lambda: "ok")
    assert sleeps  # the 3rd call within the hour forced a wait


def test_backpressure_when_queue_exceeds_depth() -> None:
    gatekeeper = ApiGatekeeper(
        _config(requests_per_minute=1, max_queue_depth=2),
        time_fn=_Clock(),
        sleep_fn=lambda _: None,
    )
    with pytest.raises(BackpressureError):
        for _ in range(6):
            gatekeeper.execute(lambda: "x")


def test_backpressure_emits_warning_alert(caplog: pytest.LogCaptureFixture) -> None:
    gatekeeper = ApiGatekeeper(
        _config(requests_per_minute=1, max_queue_depth=2),
        time_fn=_Clock(),
        sleep_fn=lambda _: None,
    )
    with caplog.at_level("WARNING", logger="bookgen.gatekeeper"), pytest.raises(BackpressureError):
        for _ in range(6):
            gatekeeper.execute(lambda: "x")
    assert any("backpressure alert" in message for message in caplog.messages)


def test_calls_logged_for_monitoring(caplog: pytest.LogCaptureFixture) -> None:
    gatekeeper = ApiGatekeeper(_config(), time_fn=_Clock(), sleep_fn=lambda _: None)
    with caplog.at_level("INFO", logger="bookgen.gatekeeper"):
        gatekeeper.execute(lambda: "ok")
    assert any("gatekeeper call #" in message for message in caplog.messages)
