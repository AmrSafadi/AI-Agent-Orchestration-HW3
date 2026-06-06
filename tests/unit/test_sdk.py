"""Tests for the BookGen SDK facade (the single entry point)."""

from __future__ import annotations

from pathlib import Path

from bookgen.sdk import BookGenSDK


def test_sdk_loads_config_and_exposes_interface() -> None:
    sdk = BookGenSDK()
    assert sdk.config.setup.project.name == "AI Agent Orchestration HW3"
    for method in ("run_crew", "generate_assets", "build_document", "generate_book"):
        assert callable(getattr(sdk, method))


def test_sdk_generate_book_dry_run_renders_main_tex() -> None:
    sdk = BookGenSDK()
    result = sdk.generate_book(dry_run=True, build_pdf=False)
    assert Path(result["main_tex"]).exists()
    assert result["compiled"] is False


def test_sdk_hooks_fire_around_stages() -> None:
    events: list[str] = []
    hooks = {
        "before_run_crew": [lambda _sdk: events.append("before_run_crew")],
        "after_run_crew": [lambda _sdk, _result: events.append("after_run_crew")],
        "after_build_document": [lambda _sdk, _result: events.append("after_build_document")],
    }
    BookGenSDK(hooks=hooks).generate_book(dry_run=True, build_pdf=False)
    assert events == ["before_run_crew", "after_run_crew", "after_build_document"]


def test_sdk_estimate_cost_returns_forecast() -> None:
    sdk = BookGenSDK()
    sdk.generate_book(dry_run=True)
    estimate = sdk.estimate_cost()
    assert estimate["model"]
    assert estimate["output_tokens"] > 0
    assert estimate["estimated_usd"] is not None and estimate["estimated_usd"] >= 0
