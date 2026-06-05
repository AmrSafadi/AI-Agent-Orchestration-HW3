"""Pydantic schemas for registry records, asset specs, and harness reports.

These complement the agent-output contracts in ``schemas.py``. Each model carries
a documented example payload via ``json_schema_extra`` and at least one validator.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class SourceRegistryEntry(BaseModel):
    """A curated bibliographic source (an entry in ``source_registry.json``)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "key": "crewai_docs",
                    "entry_type": "online",
                    "author": "CrewAI",
                    "title": "CrewAI Documentation",
                    "year": "2026",
                    "url": "https://docs.crewai.com/",
                    "note": "Framework documentation.",
                }
            ]
        }
    )

    key: str = Field(min_length=1)
    entry_type: str = Field(min_length=1)
    author: str = Field(min_length=1)
    title: str = Field(min_length=1)
    year: str = Field(min_length=1)
    url: str | None = None
    note: str = ""

    @field_validator("key")
    @classmethod
    def key_must_be_citation_safe(cls, value: str) -> str:
        """Reject citation keys with characters unsafe for LaTeX/BibTeX."""
        if not all(character.isalnum() or character in "_-:" for character in value):
            raise ValueError("citation key may contain only letters, digits, '_', '-', ':'")
        return value


class CitationReport(BaseModel):
    """Deterministic citation reconciliation result."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "bib_path": "data/references/references.bib",
                    "used_keys": ["crewai_docs"],
                    "known_keys": ["crewai_docs", "langchain_docs"],
                    "missing_keys": [],
                    "unused_keys": ["langchain_docs"],
                    "passed": True,
                }
            ]
        }
    )

    bib_path: str = Field(min_length=1)
    used_keys: list[str] = Field(default_factory=list)
    known_keys: list[str] = Field(default_factory=list)
    missing_keys: list[str] = Field(default_factory=list)
    unused_keys: list[str] = Field(default_factory=list)
    passed: bool

    @model_validator(mode="after")
    def passed_matches_missing(self) -> CitationReport:
        """Keep the passed flag consistent with the missing-keys list."""
        if self.missing_keys and self.passed:
            raise ValueError("passed cannot be True while missing_keys is non-empty")
        return self


class AssetSpec(BaseModel):
    """Specification for a deterministically generated document asset."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "asset_id": "pipeline_graph",
                    "kind": "graph",
                    "source": "matplotlib",
                    "output_path": "generated/assets/graphs/agent_pipeline_graph.png",
                    "caption": "Sequential agent pipeline.",
                }
            ]
        }
    )

    asset_id: str = Field(min_length=1)
    kind: Literal["image", "graph", "table", "formula"]
    source: Literal["matplotlib", "static", "latex", "external"]
    output_path: str = Field(min_length=1)
    caption: str | None = None


class EvidenceReport(BaseModel):
    """Final evidence summary produced after rendering and compilation."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "pdf_path": "generated/pdf/final.pdf",
                    "build_passed": True,
                    "validation_passed": True,
                    "requirement_checklist": {"cover": True, "toc": True},
                    "limitations": [],
                }
            ]
        }
    )

    pdf_path: str | None = None
    build_passed: bool = False
    validation_passed: bool = False
    requirement_checklist: dict[str, bool] = Field(default_factory=dict)
    token_summary: dict[str, int] | None = None
    limitations: list[str] = Field(default_factory=list)

    @field_validator("pdf_path")
    @classmethod
    def pdf_path_must_be_pdf(cls, value: str | None) -> str | None:
        """Require the output PDF path to end with '.pdf'."""
        if value is not None and not value.endswith(".pdf"):
            raise ValueError("pdf_path must end with '.pdf'")
        return value
