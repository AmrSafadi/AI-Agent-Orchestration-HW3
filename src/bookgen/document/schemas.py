"""Pydantic schemas for structured document artifacts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PlannedSection(BaseModel):
    """A section planned inside a chapter."""

    title: str = Field(min_length=1)
    purpose: str = Field(min_length=1)


class PlannedChapter(BaseModel):
    """A planned chapter with at least one section."""

    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    sections: list[PlannedSection] = Field(min_length=1)


class BookPlan(BaseModel):
    """Planner Agent output describing the intended book/article."""

    title: str = Field(min_length=1)
    subtitle: str | None = None
    audience: str = Field(min_length=1)
    chapters: list[PlannedChapter] = Field(min_length=1)
    required_feature_placement: dict[str, str] = Field(default_factory=dict)
    acceptance_checklist: list[str] = Field(min_length=1)
    estimated_pages: int = Field(gt=0)


class SourceCandidate(BaseModel):
    """A possible source identified by the Research Agent."""

    source_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    url: str | None = None
    notes: str = ""


class ResearchPack(BaseModel):
    """Research Agent output used as context for writing."""

    topic: str = Field(min_length=1)
    key_concepts: list[str] = Field(min_length=1)
    terminology: dict[str, str] = Field(default_factory=dict)
    source_candidates: list[SourceCandidate] = Field(default_factory=list)
    chapter_notes: dict[str, str] = Field(default_factory=dict)
    unsupported_claim_warnings: list[str] = Field(default_factory=list)


class ManuscriptSection(BaseModel):
    """Written section content."""

    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


class ManuscriptChapter(BaseModel):
    """Written chapter content."""

    title: str = Field(min_length=1)
    sections: list[ManuscriptSection] = Field(min_length=1)


class Manuscript(BaseModel):
    """Writer Agent manuscript output."""

    title: str = Field(min_length=1)
    chapters: list[ManuscriptChapter] = Field(min_length=1)
    citation_markers: list[str] = Field(default_factory=list)
    asset_placeholders: list[str] = Field(default_factory=list)
    hebrew_english_section_id: str | None = None


class ReviewReport(BaseModel):
    """Reviewer Agent output describing editorial readiness."""

    approved: bool
    checklist: dict[str, bool] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
    required_fixes: list[str] = Field(default_factory=list)


class LatexAsset(BaseModel):
    """Asset reference for LaTeX assembly."""

    asset_id: str = Field(min_length=1)
    kind: Literal["image", "graph", "table", "formula"]
    target_path: str = Field(min_length=1)
    caption: str | None = None


class LatexSpec(BaseModel):
    """LaTeX Agent output used by the deterministic renderer."""

    title: str = Field(min_length=1)
    engine: str = Field(min_length=1)
    main_template: str = Field(min_length=1)
    output_pdf: str = Field(min_length=1)
    chapter_files: list[str] = Field(min_length=1)
    assets: list[LatexAsset] = Field(default_factory=list)
    bibliography_file: str = Field(min_length=1)
    bidi_required: bool = True

    @field_validator("engine")
    @classmethod
    def engine_must_be_supported(cls, value: str) -> str:
        if value not in {"lualatex", "xelatex", "pdflatex"}:
            raise ValueError(f"unsupported LaTeX engine: {value}")
        return value


class ValidationCheck(BaseModel):
    """Single deterministic validation check result."""

    name: str = Field(min_length=1)
    passed: bool
    message: str = ""


class ValidationReport(BaseModel):
    """Final deterministic validation report."""

    passed: bool
    checks: list[ValidationCheck] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
