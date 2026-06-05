"""Tests for the render-then-compile build wiring."""

from __future__ import annotations

import json
from pathlib import Path

from bookgen.latex.build import build_document

META = {
    "author": "Sharbel",
    "course": "AI Agent Orchestration",
    "lecturer": "Dr. Segal",
    "date": "2026",
}


def _setup(tmp_path: Path, book_plan: dict, latex_spec: dict) -> None:
    intermediate = tmp_path / "generated/intermediate"
    intermediate.mkdir(parents=True)
    (intermediate / "book_plan.json").write_text(json.dumps(book_plan), encoding="utf-8")
    (intermediate / "latex_spec.json").write_text(json.dumps(latex_spec), encoding="utf-8")


def test_build_document_renders_main_tex(tmp_path, default_book_plan, default_latex_spec) -> None:
    _setup(tmp_path, default_book_plan, default_latex_spec)
    result = build_document(tmp_path, META)
    assert Path(result["main_tex"]).exists()
    assert result["compiled"] is False


def test_build_document_compile_is_graceful(
    tmp_path, default_book_plan, default_latex_spec
) -> None:
    _setup(tmp_path, default_book_plan, default_latex_spec)
    result = build_document(
        tmp_path,
        META,
        compile_after=True,
        latex_config={"engine": "no-such-engine", "bibliography_backend": "no-biber", "passes": 4},
    )
    assert result["compiled"] is False
    assert "not found" in result["message"].lower()


def test_build_document_stops_before_compile_on_unresolved_citation(
    tmp_path, default_book_plan, default_latex_spec
) -> None:
    _setup(tmp_path, default_book_plan, default_latex_spec)
    registry = tmp_path / "data/input/source_registry.json"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        json.dumps(
            [
                {
                    "key": "other_source",
                    "entry_type": "online",
                    "title": "Other",
                    "year": "2026",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = build_document(tmp_path, META, compile_after=True)

    assert result["compiled"] is False
    assert result["citation_preflight"]["missing_keys"] == ["crewai_docs"]
    assert "Unresolved citation keys" in result["message"]
