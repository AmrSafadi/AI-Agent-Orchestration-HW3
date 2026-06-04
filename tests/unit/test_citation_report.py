"""Tests for citation reconciliation reporting (used/missing/unused keys)."""

from __future__ import annotations

import json
from pathlib import Path

from bookgen.harness.citation_report import build_citation_report, write_citation_report
from bookgen.harness.citations import extract_citation_keys


def _registry(tmp_path: Path) -> Path:
    path = tmp_path / "source_registry.json"
    path.write_text(
        json.dumps(
            [
                {"key": "crewai_docs", "entry_type": "online", "title": "CrewAI Docs"},
                {"key": "langchain_docs", "entry_type": "online", "title": "LangChain Docs"},
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_extract_keys_from_markdown_and_latex() -> None:
    keys = extract_citation_keys("Markdown [@crewai_docs] and LaTeX \\cite{langchain_docs}.")
    assert keys == {"crewai_docs", "langchain_docs"}


def test_build_report_tracks_used_missing_unused(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    manuscript = tmp_path / "m.md"
    manuscript.write_text("Cites [@crewai_docs] and [@ghost].", encoding="utf-8")

    report = build_citation_report(manuscript, registry, bib_path="r.bib")

    assert report.used_keys == ["crewai_docs", "ghost"]
    assert report.missing_keys == ["ghost"]
    assert report.unused_keys == ["langchain_docs"]
    assert report.passed is False


def test_write_report_emits_json(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    manuscript = tmp_path / "m.md"
    manuscript.write_text("Cites [@crewai_docs].", encoding="utf-8")
    report = build_citation_report(manuscript, registry, bib_path="r.bib")

    out = write_citation_report(report, tmp_path / "reports" / "citation_report.json")

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["passed"] is True
    assert "langchain_docs" in data["unused_keys"]
