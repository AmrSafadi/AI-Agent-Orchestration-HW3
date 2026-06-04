"""Immutable, project-wide constants shared across packages.

This is the single source of truth for the agent roster, the artifact
names/paths, and the required document features, so the config loader, the
dry-run synthesizer, the validators, and the orchestration layer cannot drift
apart (DRY / guideline 14 modular contracts).
"""

from __future__ import annotations

from pathlib import Path

# The five specialized CrewAI agent roles, in pipeline order.
REQUIRED_AGENTS: tuple[str, ...] = ("planner", "research", "writer", "reviewer", "latex")

# The five intermediate artifacts the pipeline produces, in dependency order.
ARTIFACT_NAMES: tuple[str, ...] = (
    "book_plan",
    "research_pack",
    "manuscript",
    "review_report",
    "latex_spec",
)

# Generated runtime location for each artifact (relative to the project root).
GENERATED_ARTIFACTS: dict[str, Path] = {
    "book_plan": Path("generated/intermediate/book_plan.json"),
    "research_pack": Path("generated/intermediate/research_pack.json"),
    "manuscript": Path("generated/intermediate/manuscript.md"),
    "review_report": Path("generated/intermediate/review_report.json"),
    "latex_spec": Path("generated/intermediate/latex_spec.json"),
}

# Committed sample copy that seeds each artifact during a dry run.
SAMPLE_ARTIFACTS: dict[str, Path] = {
    "book_plan": Path("data/intermediate/sample_book_plan.json"),
    "research_pack": Path("data/intermediate/sample_research_pack.json"),
    "manuscript": Path("data/intermediate/sample_manuscript.md"),
    "review_report": Path("data/intermediate/sample_review_report.json"),
    "latex_spec": Path("data/intermediate/sample_latex_spec.json"),
}

# Required document features asserted by the validators and the review checklist.
REQUIRED_FEATURES: tuple[str, ...] = (
    "cover",
    "toc",
    "chapters",
    "citations",
    "image",
    "graph",
    "table",
    "formula",
    "hebrew_english_section",
)
