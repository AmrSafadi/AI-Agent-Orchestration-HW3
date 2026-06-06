"""Convert a strong Markdown manuscript into renderer chapter context."""

from __future__ import annotations

import re

from bookgen.document.content_quality import manuscript_quality_error
from bookgen.latex.escaping import escape_latex

CITE_PATTERN = re.compile(r"\[@([A-Za-z0-9_:-]+)\]")
TOP_LEVEL = re.compile(r"^#\s+")
CHAPTER = re.compile(r"^##\s+(.+)")
SECTION = re.compile(r"^###\s+(.+)")
CHAPTER_CITE_KEYS = ("crewai_docs", "langchain_docs", "latex_project")


def chapters_from_markdown(markdown: str) -> list[dict]:
    """Return renderable chapters if ``markdown`` is strong enough, else empty."""
    if not markdown or manuscript_quality_error(markdown):
        return []
    chapters: list[dict] = []
    current_chapter: dict | None = None
    current_section: dict | None = None

    for raw_line in _strip_markdown_fence(markdown).splitlines():
        line = raw_line.rstrip()
        if TOP_LEVEL.match(line):
            continue
        chapter_match = CHAPTER.match(line)
        section_match = SECTION.match(line)
        if chapter_match:
            current_chapter = _chapter(chapter_match.group(1))
            chapters.append(current_chapter)
            current_section = None
        elif section_match and current_chapter is not None:
            current_section = _section(section_match.group(1))
            current_chapter["sections"].append(current_section)
        elif line.strip() and current_chapter is not None:
            if current_section is None:
                current_section = _section("Overview")
                current_chapter["sections"].append(current_section)
            current_section["content_lines"].append(line.strip())

    return [_finalize_chapter(chapter, index) for index, chapter in enumerate(chapters)]


def _chapter(title: str) -> dict:
    return {"title": title.strip(), "sections": []}


def _section(title: str) -> dict:
    return {"title": title.strip(), "content_lines": []}


def _finalize_chapter(chapter: dict, index: int) -> dict:
    return {
        "title": escape_latex(chapter["title"]),
        "sections": [
            {
                "title": escape_latex(section["title"]),
                "content": _escape_markdown_content("\n\n".join(section["content_lines"])),
            }
            for section in chapter["sections"]
            if section["content_lines"]
        ],
        "show_features": index == 0,
        "cite_key": CHAPTER_CITE_KEYS[index % len(CHAPTER_CITE_KEYS)],
    }


def _escape_markdown_content(text: str) -> str:
    parts: list[str] = []
    cursor = 0
    for match in CITE_PATTERN.finditer(text):
        parts.append(escape_latex(text[cursor : match.start()]))
        parts.append(rf"\cite{{{match.group(1)}}}")
        cursor = match.end()
    parts.append(escape_latex(text[cursor:]))
    return "".join(parts)


def _strip_markdown_fence(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()
