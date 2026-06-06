"""Shared plain-text helpers used across the document and orchestration layers.

Extracted here (guideline 4.2, DRY) because the same Markdown-fence stripping
logic was previously duplicated across the content-quality, manuscript, and
artifact-normalization modules.
"""

from __future__ import annotations


def strip_markdown_fence(text: str) -> str:
    """Remove a single wrapping Markdown code fence (```), if present."""
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()
