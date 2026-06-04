"""Integration test: the dry-run path creates all expected artifacts (no API)."""

from __future__ import annotations

from pathlib import Path

from bookgen.orchestration.crew import EXPECTED_ARTIFACTS, run_crew


def test_dry_run_creates_all_expected_artifacts(tmp_path: Path) -> None:
    result = run_crew(dry_run=True, root_dir=tmp_path)

    assert result.dry_run is True
    for relative_path in EXPECTED_ARTIFACTS.values():
        assert (tmp_path / relative_path).exists(), f"missing artifact: {relative_path}"
    assert len(result.artifacts) == len(EXPECTED_ARTIFACTS)
