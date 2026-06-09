"""Dry-run artifact synthesis: refresh intermediate artifacts.

The dry-run path refreshes committed ``sample_*`` artifacts into the generated
runtime directory on every run (or writes minimal placeholders) so the
deterministic pipeline runs end-to-end without an API key and without stale
runtime state from previous experiments.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from bookgen.shared.config import project_root
from bookgen.shared.constants import GENERATED_ARTIFACTS as EXPECTED_ARTIFACTS
from bookgen.shared.constants import SAMPLE_ARTIFACTS


def create_or_reuse_dry_run_artifacts(root_dir: Path | str) -> list[Path]:
    """Refresh the expected generated artifacts for dry-run mode."""
    root = Path(root_dir)
    (root / "generated/intermediate").mkdir(parents=True, exist_ok=True)

    created_or_existing: list[Path] = []
    for artifact_name, relative_path in EXPECTED_ARTIFACTS.items():
        target = root / relative_path
        _create_dry_run_artifact(root, artifact_name, target)
        created_or_existing.append(target)
    return created_or_existing


def _create_dry_run_artifact(root: Path, artifact_name: str, target: Path) -> None:
    sample_path = SAMPLE_ARTIFACTS.get(artifact_name)
    if sample_path is not None:
        for sample_root in (root, project_root()):
            source = sample_root / sample_path
            if source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                return

    target.parent.mkdir(parents=True, exist_ok=True)
    if artifact_name == "research_pack":
        target.write_text(json.dumps(_sample_research_pack(), indent=2), encoding="utf-8")
    elif artifact_name == "review_report":
        target.write_text(json.dumps(_sample_review_report(), indent=2), encoding="utf-8")
    elif artifact_name == "manuscript":
        target.write_text(
            "# Dry Run Manuscript\n\nNo real CrewAI execution has happened.\n", encoding="utf-8"
        )
    else:
        # book_plan / latex_spec have no safe minimal placeholder (they would fail
        # schema validation downstream). Fail loudly with a clear, catchable error
        # instead of writing "{}" that crashes the build with a ValidationError.
        raise FileNotFoundError(
            f"Required sample artifact for '{artifact_name}' is missing; expected at "
            f"{SAMPLE_ARTIFACTS.get(artifact_name)} under the project root."
        )


def _sample_research_pack() -> dict[str, Any]:
    return {
        "topic": "Football Analytics and AI-Based Match Strategy",
        "key_concepts": ["xG", "event data", "tracking data", "PPDA", "pass networks"],
        "terminology": {
            "xG": "Expected-goals estimate for shot quality.",
            "PPDA": "Passes allowed per defensive action, used as a pressing proxy.",
        },
        "source_candidates": [
            {
                "source_id": "statsbomb_xg",
                "title": "StatsBomb: Introduction to Expected Goals",
                "url": "https://statsbomb.com/soccer-metrics/expected-goals-xg-explained/",
                "notes": "Reference source for expected-goals concepts.",
            }
        ],
        "chapter_notes": {
            "From Coaching Intuition To Data": "Explain how football analytics supports tactical decisions."
        },
        "unsupported_claim_warnings": [],
    }


def _sample_review_report() -> dict[str, Any]:
    return {
        "approved": True,
        "checklist": {
            "cover": True,
            "toc": True,
            "chapters": True,
            "citations": True,
            "image": True,
            "graph": True,
            "table": True,
            "formula": True,
            "hebrew_english_section": True,
        },
        "notes": ["Dry-run artifact created without CrewAI kickoff."],
        "required_fixes": [],
    }
