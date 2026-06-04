---
name: citation-discipline
description: Rules for trustworthy citations sourced only from the curated registry.
metadata:
  author: bookgen-team
  version: "1.0"
---

## Citation Discipline

1. Cite only sources present in the curated registry (`data/input/source_registry.json`).
2. Use the registry `key` as the citation marker (e.g. `[@crewai_docs]` or `\cite{crewai_docs}`).
3. Never fabricate bibliography entries, URLs, authors, or years.
4. Flag any claim that needs a source but has none as an unsupported-claim warning.

## Boundaries

- You propose and place citation markers; the deterministic Citation Manager builds the
  `.bib` file and validates that every key resolves.
