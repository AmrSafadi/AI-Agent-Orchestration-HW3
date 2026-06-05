from pathlib import Path

import pytest

from bookgen.orchestration.crew import (
    EXPECTED_ARTIFACTS,
    build_crew,
    run_crew,
)
from bookgen.shared.config import project_root
from bookgen.shared.constants import SAMPLE_ARTIFACTS


def test_crew_can_be_assembled() -> None:
    crew = build_crew()

    assert len(crew.agents) == 5
    assert len(crew.tasks) == 5
    assert str(crew.process).lower().endswith("sequential")


def test_dry_run_creates_expected_artifacts(tmp_path: Path) -> None:
    result = run_crew(dry_run=True, root_dir=tmp_path)

    assert result.dry_run is True
    assert "Dry-run completed" in result.message
    for relative_path in EXPECTED_ARTIFACTS.values():
        assert relative_path.parts[:2] == ("generated", "intermediate")
        assert (tmp_path / relative_path).exists()


def test_dry_run_refreshes_stale_artifacts(tmp_path: Path) -> None:
    stale_book_plan = tmp_path / EXPECTED_ARTIFACTS["book_plan"]
    stale_book_plan.parent.mkdir(parents=True, exist_ok=True)
    stale_book_plan.write_text("{}", encoding="utf-8")

    result = run_crew(dry_run=True, root_dir=tmp_path)

    assert result.dry_run is True
    sample_text = (project_root() / SAMPLE_ARTIFACTS["book_plan"]).read_text(encoding="utf-8")
    assert stale_book_plan.read_text(encoding="utf-8") == sample_text


def test_real_run_refuses_without_openai_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        run_crew(dry_run=False)
