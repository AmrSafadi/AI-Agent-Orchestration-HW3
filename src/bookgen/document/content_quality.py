"""Content-depth gates for real CrewAI artifacts.

Schema validation proves shape. These checks prove that a paid real run is
substantial enough to replace the deterministic submission artifacts.
"""

from __future__ import annotations

import re
from typing import Any

from bookgen.document.schemas import BookPlan, LatexSpec, ReviewReport

MIN_CHAPTERS = 5
MIN_PAGES = 15
MIN_MANUSCRIPT_CHAPTERS = 5
MIN_MANUSCRIPT_WORDS = 1600
MIN_HEBREW_CHARS = 500
REQUIRED_PLAN_FEATURES = {
    "cover",
    "toc",
    "image",
    "graph",
    "table",
    "formula",
    "hebrew_english_section",
    "citations",
}
REQUIRED_ASSET_KINDS = {"image", "graph", "table", "formula"}
PLACEHOLDER_PATTERNS = (
    "placeholder",
    "citation placeholder",
    "hebrew-english section placeholder",
    "will include",
    "to be added",
    "todo",
)


def artifact_quality_error(name: str, artifact: Any) -> str | None:
    """Return an error if a real artifact is too shallow for canonical use."""
    if name == "book_plan" and isinstance(artifact, BookPlan):
        return _book_plan_error(artifact)
    if name == "manuscript" and isinstance(artifact, str):
        return manuscript_quality_error(artifact)
    if name == "review_report" and isinstance(artifact, ReviewReport):
        return None if artifact.approved else "review report did not approve the manuscript"
    if name == "latex_spec" and isinstance(artifact, LatexSpec):
        return _latex_spec_error(artifact)
    return None


def manuscript_quality_error(text: str) -> str | None:
    """Return why Markdown manuscript text is not ready for PDF rendering."""
    stripped = _strip_markdown_fence(text)
    lowered = stripped.lower()
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern in lowered:
            return f"manuscript contains placeholder text: {pattern}"
    if _markdown_chapter_count(stripped) < MIN_MANUSCRIPT_CHAPTERS:
        return f"manuscript needs at least {MIN_MANUSCRIPT_CHAPTERS} markdown chapters"
    if _word_count(stripped) < MIN_MANUSCRIPT_WORDS:
        return f"manuscript needs at least {MIN_MANUSCRIPT_WORDS} words"
    if _hebrew_char_count(stripped) < MIN_HEBREW_CHARS:
        return f"manuscript needs at least {MIN_HEBREW_CHARS} Hebrew characters"
    return None


def _book_plan_error(plan: BookPlan) -> str | None:
    if len(plan.chapters) < MIN_CHAPTERS:
        return f"book plan needs at least {MIN_CHAPTERS} chapters"
    if plan.estimated_pages < MIN_PAGES:
        return f"book plan must target at least {MIN_PAGES} pages"
    feature_keys = {key.lower() for key in plan.required_feature_placement}
    missing = sorted(REQUIRED_PLAN_FEATURES - feature_keys)
    if missing:
        return f"book plan missing required feature placement: {', '.join(missing)}"
    return None


def _latex_spec_error(spec: LatexSpec) -> str | None:
    if spec.engine != "lualatex":
        return "LaTeX spec must use lualatex for Hebrew/BiDi output"
    if not spec.bidi_required:
        return "LaTeX spec must require BiDi support"
    asset_kinds = {asset.kind for asset in spec.assets}
    missing = sorted(REQUIRED_ASSET_KINDS - asset_kinds)
    if missing:
        return f"LaTeX spec missing required asset kinds: {', '.join(missing)}"
    return None


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


def _markdown_chapter_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if re.match(r"^##\s+\S", line))


def _word_count(text: str) -> int:
    return len(re.findall(r"[\w\u0590-\u05FF]+", text, flags=re.UNICODE))


def _hebrew_char_count(text: str) -> int:
    return len(re.findall(r"[\u0590-\u05FF]", text))
