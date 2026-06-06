# Specialized PRD — Citation Management & BibTeX Generation

Dedicated PRD per submission guideline 2.3 for a central mechanism. Parent
requirements: [PRD.md](PRD.md). Implementation: `src/bookgen/harness/citations.py`.

## 1. Mechanism Description and Background

Citation management is deterministic by design (it is **not** an agent): a model
must not invent bibliography entries or citation keys. The mechanism reads a
curated source registry, generates a valid `.bib` file, and validates that every
citation marker in the manuscript resolves to a known source.

**Background.** A reliable bibliography requires (a) a single curated source of
truth for sources, (b) syntactically valid BibTeX with safe escaping, and
(c) a reconciliation step that fails loudly on unknown or fabricated keys before
the document is compiled.

## 2. Inputs / Outputs

**Inputs**
- `data/input/source_registry.json`: curated sources (id, title, author, year,
  url, type).
- Manuscript / reviewed manuscript: citation markers using source ids.

> Canonical manuscript format (T477): the canonical authored manuscript is
> `data/intermediate/sample_book_plan.json` (the BookPlan / `book_plan.json`
> contract), which the renderer renders from; `sample_manuscript.md` is only an
> auxiliary sample (and the source of Markdown citation-marker extraction tests),
> not the rendered document.

**Outputs**
- `data/references/references.bib`: generated BibTeX (git-ignored; regenerated
  from the registry).
- A citation report listing unresolved or unused keys.

> Naming note: the canonical report name is standardized in code as
> `citation_report.json` (`src/bookgen/harness/citation_report.py` →
> `generated/reports/citation_report.json`). The legacy
> `citation_registry.json` name is only a stale reference in the root
> `ARCHITECTURE.md`, not an open decision.

## 3. Requirements and Performance Metrics

- Every citation marker in the manuscript maps to a known source id.
- Every cited source appears in `references.bib`; no fabricated entries.
- No invalid/duplicate BibTeX keys; special characters escaped.
- Citation-key extraction works for both Markdown and LaTeX manuscripts.
- Regeneration is idempotent: same registry input ⇒ same `.bib` output.

## 4. Constraints and Limitations

- The Research agent may only *propose* source candidates; it must not write
  `.bib` files (separation of judgment from deterministic output).
- `references.bib` is generated, so it is git-ignored; `data/references/references.bib`
  is now committed for grader visibility (T072 done; `.gitignore` re-includes that
  one file).
- Citation-key extraction is ASCII/Latin-key based and is unaffected by the
  Hebrew-primary (RTL) manuscript body.
- Keep the module ≤ 150 code lines; factor escaping into a shared helper if it
  grows.

## 5. Alternatives Considered

| Alternative | Why not chosen |
|---|---|
| A dedicated Citation Agent | Citation correctness must be deterministic, not improvised. |
| Hand-written `.bib` | Not reproducible; drifts from the manuscript. |
| Inline citations without BibTeX | Loses biber cross-referencing and a real bibliography. |

## 6. Success Criteria and Test Scenarios

**Success criteria.** From a curated registry and a manuscript, the mechanism
produces a valid `references.bib` and a citation report with zero unresolved
keys, ready for the multi-pass LaTeX build.

**Test scenarios** (`tests/unit/test_citations.py`):
- Generate `.bib` from a sample registry and assert valid entries and keys.
- Extract citation keys from sample Markdown and LaTeX text.
- Assert an unknown citation key is reported as unresolved.
- Assert special characters in titles/authors are escaped in the `.bib`.
