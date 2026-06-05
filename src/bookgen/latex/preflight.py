"""Pre-compile checks for rendered LaTeX documents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bookgen.harness.citations import extract_citation_keys, load_source_registry


@dataclass(frozen=True)
class CitationPreflight:
    """Citation keys found in the rendered LaTeX and whether all are known."""

    used_keys: set[str]
    known_keys: set[str]
    missing_keys: set[str]

    @property
    def passed(self) -> bool:
        """Return whether all rendered citation keys exist in the source registry."""
        return not self.missing_keys


def validate_rendered_citations(
    tex_path: Path | str,
    registry_path: Path | str,
) -> CitationPreflight:
    """Validate rendered LaTeX citation keys before invoking the compiler."""
    tex_text = Path(tex_path).read_text(encoding="utf-8")
    used_keys = extract_citation_keys(tex_text)
    known_keys = set(load_source_registry(registry_path))
    return CitationPreflight(
        used_keys=used_keys,
        known_keys=known_keys,
        missing_keys=used_keys - known_keys,
    )
