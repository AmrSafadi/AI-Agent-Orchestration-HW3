from pathlib import Path

import pytest

from bookgen.orchestration.crew import (
    EXPECTED_ARTIFACTS,
    create_document_generation_crew,
    run_crew,
)


def test_crew_can_be_assembled() -> None:
    crew = create_document_generation_crew()

    assert len(crew.agents) == 5
    assert len(crew.tasks) == 5
    assert str(crew.process).lower().endswith("sequential")


def test_dry_run_creates_expected_artifacts(tmp_path: Path) -> None:
    result = run_crew(dry_run=True, root_dir=tmp_path)

    assert result.dry_run is True
    assert "Dry-run completed" in result.message
    for relative_path in EXPECTED_ARTIFACTS.values():
        assert (tmp_path / relative_path).exists()


def test_real_run_refuses_without_openai_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        run_crew(dry_run=False)
