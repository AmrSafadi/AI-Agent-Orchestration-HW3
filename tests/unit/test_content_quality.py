"""Tests for the deterministic content-depth gates (offline error branches)."""

from __future__ import annotations

from bookgen.document.content_quality import artifact_quality_error, manuscript_quality_error
from bookgen.document.schemas import (
    BookPlan,
    LatexAsset,
    LatexSpec,
    PlannedChapter,
    PlannedSection,
    ReviewReport,
)

FEATURES = {
    "cover",
    "toc",
    "image",
    "graph",
    "table",
    "formula",
    "hebrew_english_section",
    "citations",
}
KINDS = ("image", "graph", "table", "formula")


def _plan(chapters: int = 5, pages: int = 16, features: set[str] = FEATURES) -> BookPlan:
    return BookPlan(
        title="T",
        audience="A",
        chapters=[
            PlannedChapter(
                title=f"C{i}", summary="s", sections=[PlannedSection(title="t", purpose="p")]
            )
            for i in range(chapters)
        ],
        required_feature_placement=dict.fromkeys(features, "C1"),
        acceptance_checklist=["cover"],
        estimated_pages=pages,
    )


def _spec(engine: str = "lualatex", bidi: bool = True, kinds: tuple[str, ...] = KINDS) -> LatexSpec:
    return LatexSpec(
        title="T",
        engine=engine,
        main_template="m",
        output_pdf="o.pdf",
        chapter_files=["c.tex"],
        assets=[LatexAsset(asset_id=k, kind=k, target_path=f"{k}.x") for k in kinds],
        bibliography_file="r.bib",
        bidi_required=bidi,
    )


def _manuscript(chapters: int = 5, word: str = "סוכן", repeats: int = 400) -> str:
    body = " ".join([word] * repeats)
    return "\n\n".join(f"## C{i}\n\n### S{i}\n\n{body}" for i in range(chapters))


def test_book_plan_branches() -> None:
    assert "at least 5 chapters" in artifact_quality_error("book_plan", _plan(chapters=4))
    assert "at least 15 pages" in artifact_quality_error("book_plan", _plan(pages=10))
    assert "missing required feature" in artifact_quality_error(
        "book_plan", _plan(features={"cover", "toc"})
    )
    assert artifact_quality_error("book_plan", _plan()) is None


def test_latex_spec_branches() -> None:
    assert "lualatex" in artifact_quality_error("latex_spec", _spec(engine="xelatex"))
    assert "BiDi" in artifact_quality_error("latex_spec", _spec(bidi=False))
    assert "missing required asset kinds" in artifact_quality_error(
        "latex_spec", _spec(kinds=("image", "graph"))
    )
    assert artifact_quality_error("latex_spec", _spec()) is None


def test_review_report_branches() -> None:
    assert "did not approve" in artifact_quality_error(
        "review_report", ReviewReport(approved=False)
    )
    assert artifact_quality_error("review_report", ReviewReport(approved=True)) is None


def test_manuscript_branches() -> None:
    assert "placeholder" in manuscript_quality_error("## A\n\nTODO here.")
    assert "markdown chapters" in manuscript_quality_error("## One\n\nsome real words here.")
    assert "1600 words" in manuscript_quality_error(_manuscript(word="word", repeats=2))
    assert "Hebrew characters" in manuscript_quality_error(_manuscript(word="word", repeats=400))
    assert manuscript_quality_error(_manuscript()) is None


def test_artifact_quality_error_dispatches_manuscript() -> None:
    assert "placeholder" in artifact_quality_error("manuscript", "## A\n\nTODO")
    assert artifact_quality_error("unknown", object()) is None
