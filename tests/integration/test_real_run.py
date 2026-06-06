"""Key-guarded integration test for the real (API-backed) CrewAI run.

This test is skipped unless ``OPENAI_API_KEY`` is set, so the default test suite
never depends on a paid API, the network, or the CrewAI provider (guideline:
tests must be deterministic and offline).
"""

from __future__ import annotations

import os

import pytest

from bookgen.orchestration.crew import run_crew


@pytest.mark.skipif(
    not (os.getenv("OPENAI_API_KEY") and os.getenv("BOOKGEN_RUN_REAL_INTEGRATION") == "1"),
    reason=(
        "requires OPENAI_API_KEY and BOOKGEN_RUN_REAL_INTEGRATION=1; "
        "real integration tests are paid and opt-in"
    ),
)
def test_real_run_executes_and_returns_output() -> None:
    result = run_crew(dry_run=False)
    assert result.dry_run is False
    assert result.output is not None
