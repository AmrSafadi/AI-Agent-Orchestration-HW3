import json
from pathlib import Path

from bookgen.harness.citations import generate_references_bib, validate_citation_keys


def test_citation_manager_creates_references_bib(tmp_path: Path) -> None:
    registry_path = tmp_path / "source_registry.json"
    output_path = tmp_path / "references.bib"
    registry_path.write_text(
        json.dumps(
            [
                {
                    "key": "crewai_docs",
                    "entry_type": "online",
                    "author": "CrewAI",
                    "title": "CrewAI Documentation",
                    "year": "2026",
                    "url": "https://docs.crewai.com/",
                }
            ]
        ),
        encoding="utf-8",
    )

    generated_path = generate_references_bib(registry_path, output_path)

    assert generated_path == output_path
    assert "@online{crewai_docs" in output_path.read_text(encoding="utf-8")


def test_citation_validation_reports_missing_keys(tmp_path: Path) -> None:
    registry_path = tmp_path / "source_registry.json"
    manuscript_path = tmp_path / "manuscript.md"
    registry_path.write_text(
        json.dumps(
            [
                {
                    "key": "crewai_docs",
                    "entry_type": "online",
                    "title": "CrewAI Documentation",
                }
            ]
        ),
        encoding="utf-8",
    )
    manuscript_path.write_text(
        "This cites a known source [@crewai_docs] and a missing source [@missing_source].",
        encoding="utf-8",
    )

    result = validate_citation_keys(manuscript_path, registry_path)

    assert not result.passed
    assert result.missing_keys == {"missing_source"}
