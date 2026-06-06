"""Helper functions for real-run artifact normalization."""

from __future__ import annotations

import re
from typing import Any


def collect(chapters: list[dict[str, Any]], key: str) -> list[Any]:
    collected = []
    for chapter in chapters:
        value = chapter.get(key, [])
        collected.extend(value if isinstance(value, list) else [value])
    return collected


def merge_maps(chapters: list[dict[str, Any]], key: str) -> dict[str, str]:
    merged: dict[str, str] = {}
    for chapter in chapters:
        value = chapter.get(key, {})
        if isinstance(value, dict):
            merged.update({str(k): stringify(v) for k, v in value.items()})
    return merged


def sources(items: list[Any]) -> list[dict[str, str | None]]:
    return [
        {
            "source_id": slug(item, index),
            "title": stringify(item),
            "url": None,
            "notes": "",
        }
        for index, item in enumerate(items, start=1)
    ]


def chapter_notes(chapters: list[dict[str, Any]]) -> dict[str, str]:
    notes = {}
    for chapter in chapters:
        title = chapter.get("chapterTitle") or chapter.get("title") or "Untitled Chapter"
        notes[str(title)] = stringify(chapter.get("chapterNotes", ""))
    return notes


def assets(references: dict[str, Any]) -> list[dict[str, str]]:
    figures = references.get("figures", []) if isinstance(references, dict) else []
    found = [asset("course_concept_image", "image", figures[0])] if figures else []
    if len(figures) > 1:
        found.append(asset("agent_pipeline_graph", "graph", figures[1]))
    return found


def asset(asset_id: str, kind: str, target_path: str) -> dict[str, str]:
    return {"asset_id": asset_id, "kind": kind, "target_path": target_path, "caption": kind}


def string_map(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): stringify(item) for key, item in value.items()}


def flatten_values(value: Any) -> list[str]:
    if isinstance(value, list):
        return [stringify(item) for item in value]
    if isinstance(value, dict):
        return [f"{key}: {stringify(item)}" for key, item in value.items()]
    return [stringify(value)] if value else []


def stringify(value: Any) -> str:
    if isinstance(value, dict):
        return "; ".join(f"{key}: {stringify(item)}" for key, item in value.items())
    if isinstance(value, list):
        return "; ".join(stringify(item) for item in value)
    return str(value)


def unique(values: list[Any]) -> list[str]:
    result = []
    for value in values:
        text = stringify(value)
        if text and text not in result:
            result.append(text)
    return result


def slug(value: Any, index: int) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", stringify(value).lower()).strip("_")
    return text[:48] or f"source_{index}"
