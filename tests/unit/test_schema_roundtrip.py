"""Round-trip (serialize -> parse) and validator tests for every artifact schema."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from bookgen.document.report_schemas import (
    AssetSpec,
    CitationReport,
    EvidenceReport,
    SourceRegistryEntry,
)
from bookgen.document.schemas import (
    BookPlan,
    LatexSpec,
    Manuscript,
    ManuscriptChapter,
    ManuscriptSection,
    PlannedChapter,
    PlannedSection,
    ResearchPack,
    ReviewReport,
    ValidationCheck,
    ValidationReport,
)

CASES: list[BaseModel] = [
    BookPlan(
        title="AI Agent Orchestration",
        audience="Course evaluator",
        chapters=[
            PlannedChapter(
                title="Foundations",
                summary="Intro.",
                sections=[PlannedSection(title="CrewAI", purpose="Explain.")],
            )
        ],
        acceptance_checklist=["cover"],
        estimated_pages=15,
    ),
    ResearchPack(topic="Agents", key_concepts=["Agent", "Crew"]),
    Manuscript(
        title="Agents",
        chapters=[
            ManuscriptChapter(
                title="Intro",
                sections=[ManuscriptSection(title="Why", content="Because.")],
            )
        ],
    ),
    ReviewReport(approved=True, checklist={"cover": True}),
    LatexSpec(
        title="Agents",
        engine="lualatex",
        main_template="main.tex.j2",
        output_pdf="generated/pdf/final.pdf",
        chapter_files=["chapters/chapter_01.tex"],
        bibliography_file="data/references/references.bib",
    ),
    ValidationReport(passed=True, checks=[ValidationCheck(name="feature:cover", passed=True)]),
    CitationReport(
        bib_path="data/references/references.bib", used_keys=["crewai_docs"], passed=True
    ),
    SourceRegistryEntry(
        key="crewai_docs",
        entry_type="online",
        author="CrewAI",
        title="Docs",
        year="2026",
        url="https://docs.crewai.com/",
    ),
    AssetSpec(asset_id="g1", kind="graph", source="matplotlib", output_path="g.png"),
    EvidenceReport(pdf_path="generated/pdf/final.pdf", build_passed=True),
]


@pytest.mark.parametrize("model", CASES, ids=lambda model: type(model).__name__)
def test_roundtrip_preserves_data(model: BaseModel) -> None:
    reparsed = type(model).model_validate_json(model.model_dump_json())
    assert reparsed.model_dump() == model.model_dump()


def test_latex_spec_rejects_unknown_engine() -> None:
    with pytest.raises(ValidationError):
        LatexSpec(
            title="Agents",
            engine="winword",
            main_template="main.tex.j2",
            output_pdf="final.pdf",
            chapter_files=["c.tex"],
            bibliography_file="r.bib",
        )


def test_citation_report_rejects_inconsistent_passed() -> None:
    with pytest.raises(ValidationError):
        CitationReport(bib_path="r.bib", missing_keys=["ghost"], passed=True)


def test_source_registry_entry_rejects_unsafe_key() -> None:
    with pytest.raises(ValidationError):
        SourceRegistryEntry(
            key="bad key!",
            entry_type="online",
            author="A",
            title="T",
            year="2026",
        )


def test_evidence_report_rejects_non_pdf_path() -> None:
    with pytest.raises(ValidationError):
        EvidenceReport(pdf_path="final.txt")
