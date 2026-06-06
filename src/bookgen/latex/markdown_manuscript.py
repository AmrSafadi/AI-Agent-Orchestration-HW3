"""Convert a strong Markdown manuscript into renderer chapter context.

Prose that appears before the first ``## Chapter`` heading is preserved as an
introduction section of the first chapter (never silently dropped), and common
inline Markdown (``**bold**``, ``*italic*``, ``- `` bullet lists) is converted to
LaTeX rather than emitted verbatim.
"""

from __future__ import annotations

import re

from bookgen.document.content_quality import manuscript_quality_error
from bookgen.latex.escaping import escape_latex
from bookgen.shared.text import strip_markdown_fence

CITE_PATTERN = re.compile(r"\[@([A-Za-z0-9_:-]+)\]")
TOP_LEVEL = re.compile(r"^#\s+")
CHAPTER = re.compile(r"^##\s+(.+)")
SECTION = re.compile(r"^###\s+(.+)")
BOLD = re.compile(r"\*\*(.+?)\*\*")
ITALIC = re.compile(r"\*(.+?)\*")
CHAPTER_CITE_KEYS = ("crewai_docs", "langchain_docs", "latex_project")
INTRO_TITLE = "מבוא"  # "מבוא" (Introduction)


def chapters_from_markdown(markdown: str) -> list[dict]:
    """Return renderable chapters if ``markdown`` is strong enough, else empty."""
    if not markdown or manuscript_quality_error(markdown):
        return []
    chapters: list[dict] = []
    current_chapter: dict | None = None
    current_section: dict | None = None
    intro_lines: list[str] = []

    for raw_line in strip_markdown_fence(markdown).splitlines():
        line = raw_line.rstrip()
        if TOP_LEVEL.match(line):
            continue
        chapter_match = CHAPTER.match(line)
        section_match = SECTION.match(line)
        if chapter_match:
            current_chapter = _chapter(chapter_match.group(1))
            if not chapters and intro_lines:
                current_chapter["sections"].append(_intro_section(intro_lines))
            chapters.append(current_chapter)
            current_section = None
        elif section_match and current_chapter is not None:
            current_section = _section(section_match.group(1))
            current_chapter["sections"].append(current_section)
        elif line.strip():
            if current_chapter is None:
                intro_lines.append(line.strip())
            else:
                if current_section is None:
                    current_section = _section("Overview")
                    current_chapter["sections"].append(current_section)
                current_section["content_lines"].append(line.strip())

    return [_finalize_chapter(chapter, index) for index, chapter in enumerate(chapters)]


def _chapter(title: str) -> dict:
    """Create an empty chapter accumulator."""
    return {"title": title.strip(), "sections": []}


def _section(title: str) -> dict:
    """Create an empty section accumulator."""
    return {"title": title.strip(), "content_lines": []}


def _intro_section(lines: list[str]) -> dict:
    """Wrap pre-first-chapter prose into an introduction section."""
    section = _section(INTRO_TITLE)
    section["content_lines"] = list(lines)
    return section


def _finalize_chapter(chapter: dict, index: int) -> dict:
    """Escape/render a chapter accumulator into renderer chapter context."""
    return {
        "title": escape_latex(chapter["title"]),
        "sections": [
            {
                "title": escape_latex(section["title"]),
                "content": _render_section_content(section["content_lines"]),
            }
            for section in chapter["sections"]
            if section["content_lines"]
        ],
        "show_features": index == 0,
        "cite_key": CHAPTER_CITE_KEYS[index % len(CHAPTER_CITE_KEYS)],
    }


def _render_section_content(lines: list[str]) -> str:
    """Render section lines to LaTeX, grouping ``- `` runs into itemize blocks."""
    blocks: list[str] = []
    bullets: list[str] = []
    for line in lines:
        if line.startswith("- "):
            bullets.append(line[2:].strip())
            continue
        if bullets:
            blocks.append(_itemize(bullets))
            bullets = []
        blocks.append(_inline(line))
    if bullets:
        blocks.append(_itemize(bullets))
    return "\n\n".join(blocks)


def _itemize(items: list[str]) -> str:
    """Render bullet items as a LaTeX itemize environment."""
    rows = "\n".join(rf"\item {_inline(item)}" for item in items)
    return "\\begin{itemize}\n" + rows + "\n\\end{itemize}"


def _inline(text: str) -> str:
    """Escape text and convert inline **bold**/*italic* to LaTeX commands."""
    rendered = _escape_with_citations(text)
    rendered = BOLD.sub(r"\\textbf{\1}", rendered)
    rendered = ITALIC.sub(r"\\emph{\1}", rendered)
    return rendered


def _escape_with_citations(text: str) -> str:
    """Escape text while turning ``[@key]`` markers into ``\\cite{key}``."""
    parts: list[str] = []
    cursor = 0
    for match in CITE_PATTERN.finditer(text):
        parts.append(escape_latex(text[cursor : match.start()]))
        parts.append(rf"\cite{{{match.group(1)}}}")
        cursor = match.end()
    parts.append(escape_latex(text[cursor:]))
    return "".join(parts)
