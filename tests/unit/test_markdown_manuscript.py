"""Tests for Markdown -> chapter-context conversion (no content is dropped)."""

from __future__ import annotations

from bookgen.latex.markdown_manuscript import chapters_from_markdown


def _strong(intro: str = "", body_word: str = "סוכן") -> str:
    chapters = []
    for index in range(1, 6):
        body = " ".join([body_word] * 330)
        chapters.append(
            f"## Chapter {index}\n\n### Section {index}\n\n{body} point {index} [@crewai_docs]."
        )
    head = f"# Title\n\n{intro}\n\n" if intro else "# Title\n\n"
    return head + "\n\n".join(chapters)


def test_shallow_markdown_returns_empty() -> None:
    assert chapters_from_markdown("# T\n\n## One\n\nPlaceholder.") == []


def test_pre_chapter_prose_is_preserved_as_intro() -> None:
    chapters = chapters_from_markdown(_strong(intro="An important framing sentence."))
    assert chapters, "a strong manuscript should yield chapters"
    first_sections = chapters[0]["sections"]
    joined = " ".join(section["content"] for section in first_sections)
    assert "An important framing sentence." in joined


def test_inline_bold_italic_and_lists_convert_to_latex() -> None:
    body_word = "מילה"
    body = " ".join([body_word] * 330)
    markdown = (
        "# Title\n\n"
        f"## Chapter 1\n\n### Section 1\n\nThis is **bold** and *italic*. {body} [@crewai_docs].\n"
        "- first bullet\n- second bullet\n\n"
        + "\n\n".join(
            f"## Chapter {i}\n\n### Section {i}\n\n{body} [@crewai_docs]." for i in range(2, 6)
        )
    )
    content = chapters_from_markdown(markdown)[0]["sections"][0]["content"]
    assert "\\textbf{bold}" in content
    assert "\\emph{italic}" in content
    assert "\\begin{itemize}" in content
    assert "\\item first bullet" in content


def test_citation_markers_become_cite_commands() -> None:
    content = chapters_from_markdown(_strong())[0]["sections"][0]["content"]
    assert "\\cite{crewai_docs}" in content
