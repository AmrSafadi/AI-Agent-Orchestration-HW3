"""Deterministic citation registry and BibTeX generation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY_PATH = Path("data/input/source_registry.json")
DEFAULT_BIB_PATH = Path("data/references/references.bib")

CITE_COMMAND_PATTERN = re.compile(r"\\cite[a-zA-Z*]*\{([^}]+)\}")
MARKDOWN_CITATION_PATTERN = re.compile(r"(?<![\w.-])@([A-Za-z][A-Za-z0-9:_-]*)")


@dataclass(frozen=True)
class SourceRecord:
    """Single curated source registry entry."""

    key: str
    entry_type: str
    fields: dict[str, str]


@dataclass(frozen=True)
class CitationValidationResult:
    """Result of deterministic citation-key validation."""

    used_keys: set[str]
    known_keys: set[str]
    missing_keys: set[str]

    @property
    def passed(self) -> bool:
        """Return whether every used citation key exists in the registry."""
        return not self.missing_keys


def load_source_registry(
    registry_path: Path | str = DEFAULT_REGISTRY_PATH,
) -> dict[str, SourceRecord]:
    """Load curated source records keyed by citation key."""
    path = Path(registry_path)
    with path.open("r", encoding="utf-8") as handle:
        raw_sources = json.load(handle)

    if not isinstance(raw_sources, list):
        raise ValueError("Source registry must be a JSON list")

    records: dict[str, SourceRecord] = {}
    for raw_source in raw_sources:
        if not isinstance(raw_source, dict):
            raise ValueError("Each source registry entry must be a JSON object")

        key = _required_string(raw_source, "key")
        entry_type = _required_string(raw_source, "entry_type")
        fields = {
            field_key: str(field_value)
            for field_key, field_value in raw_source.items()
            if field_key not in {"key", "entry_type"} and field_value not in {None, ""}
        }
        if not fields:
            raise ValueError(f"Source '{key}' must contain at least one BibTeX field")
        if key in records:
            raise ValueError(f"Duplicate source key: {key}")

        records[key] = SourceRecord(key=key, entry_type=entry_type, fields=fields)

    return records


def generate_references_bib(
    registry_path: Path | str = DEFAULT_REGISTRY_PATH,
    output_path: Path | str = DEFAULT_BIB_PATH,
) -> Path:
    """Generate a BibTeX file from the curated source registry."""
    records = load_source_registry(registry_path)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    entries = [_format_bibtex_entry(record) for record in records.values()]
    path.write_text("\n\n".join(entries) + "\n", encoding="utf-8")
    return path


def extract_citation_keys(manuscript_text: str) -> set[str]:
    """Extract citation keys from Markdown-style and LaTeX-style citations."""
    keys: set[str] = set()

    for command_match in CITE_COMMAND_PATTERN.finditer(manuscript_text):
        for key in command_match.group(1).split(","):
            cleaned_key = key.strip()
            if cleaned_key:
                keys.add(cleaned_key)

    keys.update(MARKDOWN_CITATION_PATTERN.findall(manuscript_text))
    return keys


def validate_citation_keys(
    manuscript_path: Path | str,
    registry_path: Path | str = DEFAULT_REGISTRY_PATH,
) -> CitationValidationResult:
    """Validate citations used in a manuscript against the curated source registry."""
    manuscript_text = Path(manuscript_path).read_text(encoding="utf-8")
    used_keys = extract_citation_keys(manuscript_text)
    known_keys = set(load_source_registry(registry_path))
    return CitationValidationResult(
        used_keys=used_keys,
        known_keys=known_keys,
        missing_keys=used_keys - known_keys,
    )


def _format_bibtex_entry(record: SourceRecord) -> str:
    fields = ",\n".join(
        f"  {field_key} = {{{_escape_bibtex(str(field_value))}}}"
        for field_key, field_value in sorted(record.fields.items())
    )
    return f"@{record.entry_type}{{{record.key},\n{fields}\n}}"


def _escape_bibtex(value: str) -> str:
    return value.replace("\\", "\\textbackslash{}").replace("{", "\\{").replace("}", "\\}")


def _required_string(source: dict[str, Any], key: str) -> str:
    value = source.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Source registry entry is missing required string field: {key}")
    return value.strip()
