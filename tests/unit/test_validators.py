import json
from pathlib import Path

from bookgen.document.validators import validate_required_document_features


def test_validator_detects_missing_required_features(tmp_path: Path) -> None:
    book_plan_path = tmp_path / "book_plan.json"
    latex_spec_path = tmp_path / "latex_spec.json"
    manuscript_path = tmp_path / "manuscript.md"

    book_plan_path.write_text(
        json.dumps(
            {
                "title": "AI Agent Orchestration",
                "audience": "Course evaluator",
                "chapters": [
                    {
                        "title": "Foundations",
                        "summary": "A short chapter.",
                        "sections": [
                            {
                                "title": "CrewAI",
                                "purpose": "Explain the basics.",
                            }
                        ],
                    }
                ],
                "required_feature_placement": {
                    "cover": "front matter",
                    "toc": "front matter",
                },
                "acceptance_checklist": ["cover", "toc"],
                "estimated_pages": 15,
            }
        ),
        encoding="utf-8",
    )
    latex_spec_path.write_text(
        json.dumps(
            {
                "title": "AI Agent Orchestration",
                "engine": "lualatex",
                "main_template": "main.tex.j2",
                "output_pdf": "generated/pdf/final.pdf",
                "chapter_files": ["chapters/chapter_01.tex"],
                "assets": [],
                "bibliography_file": "data/references/references.bib",
                "bidi_required": True,
            }
        ),
        encoding="utf-8",
    )
    manuscript_path.write_text("This manuscript cites CrewAI [@crewai_docs].", encoding="utf-8")

    report = validate_required_document_features(book_plan_path, latex_spec_path, manuscript_path)

    assert not report.passed
    assert any("feature:image" in error for error in report.errors)
    assert any("feature:graph" in error for error in report.errors)
    assert any("feature:hebrew_english_section" in error for error in report.errors)
