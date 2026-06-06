"""Conservative normalization for common real-LLM artifact shape drift."""

from __future__ import annotations

from typing import Any

from bookgen.orchestration.artifact_normalization_utils import (
    assets,
    chapter_notes,
    collect,
    flatten_values,
    merge_maps,
    sources,
    string_map,
    stringify,
    unique,
)


def normalize_artifact_payload(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Return a schema-shaped payload for known real-run variants."""
    normalizers = {
        "book_plan": _book_plan,
        "research_pack": _research_pack,
        "review_report": _review_report,
        "latex_spec": _latex_spec,
    }
    return normalizers.get(name, lambda value: value)(payload)


def _book_plan(payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)
    data["audience"] = stringify(data.get("audience", ""))
    data.setdefault("chapters", [_chapter(chapter) for chapter in data.get("chapterOutline", [])])
    data.setdefault(
        "required_feature_placement",
        string_map(data.get("requiredFeaturePlacement", {})),
    )
    data.setdefault("acceptance_checklist", data.get("acceptanceChecklist", []))
    data.setdefault("estimated_pages", data.get("estimatedPageCount", data.get("estimated_pages")))
    return data


def _chapter(chapter: dict[str, Any]) -> dict[str, Any]:
    title = chapter.get("title") or chapter.get("chapterTitle") or "Untitled Chapter"
    sections = chapter.get("sections", [])
    return {
        "title": title,
        "summary": chapter.get("summary") or f"Chapter about {title}.",
        "sections": [_section(section) for section in sections],
    }


def _section(section: Any) -> dict[str, str]:
    if isinstance(section, dict):
        title = section.get("title") or section.get("sectionTitle") or "Untitled Section"
        purpose = section.get("purpose") or section.get("summary") or stringify(section)
        return {"title": title, "purpose": purpose}
    title = str(section)
    return {"title": title, "purpose": f"Explain {title} in the chapter context."}


def _research_pack(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("topic") and payload.get("key_concepts"):
        return payload
    chapters = payload.get("chapters", [])
    return {
        "topic": payload.get("topic") or payload.get("title") or "AI Agent Orchestration",
        "key_concepts": unique(collect(chapters, "keyConcepts")),
        "terminology": merge_maps(chapters, "terminology"),
        "source_candidates": sources(collect(chapters, "sourceCandidates")),
        "chapter_notes": chapter_notes(chapters),
        "unsupported_claim_warnings": unique(collect(chapters, "unsupportedClaimWarnings")),
    }


def _review_report(payload: dict[str, Any]) -> dict[str, Any]:
    status = str(payload.get("approval_status", "")).lower()
    return {
        "approved": payload.get("approved", status in {"approved", "accepted", "true", "yes"}),
        "checklist": payload.get("checklist") or payload.get("checklist_results") or {},
        "notes": flatten_values(payload.get("notes", [])),
        "required_fixes": flatten_values(payload.get("required_fixes", [])),
    }


def _latex_spec(payload: dict[str, Any]) -> dict[str, Any]:
    bidi_required = payload.get(
        "bidi_required", payload.get("bidi_settings", {}).get("use_bidi", True)
    )
    engine = payload.get("engine") or "lualatex"
    if bidi_required and engine == "pdflatex":
        engine = "lualatex"
    return {
        "title": payload.get("title") or "AI Agent Orchestration",
        "engine": engine,
        "main_template": payload.get("main_template") or payload.get("template") or "main.tex.j2",
        "output_pdf": payload.get("output_pdf")
        or payload.get("output_pdf_path")
        or "generated/pdf/final.pdf",
        "chapter_files": payload.get("chapter_files") or ["chapters/chapter_01.tex"],
        "assets": payload.get("assets") or assets(payload.get("asset_references", {})),
        "bibliography_file": payload.get("bibliography_file") or "data/references/references.bib",
        "bidi_required": bidi_required,
    }
