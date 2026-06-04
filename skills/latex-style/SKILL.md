---
name: latex-style
description: House style and Hebrew-English BiDi rules for professional, compilable LaTeX content.
metadata:
  author: bookgen-team
  version: "1.0"
---

## LaTeX House Style

1. Use semantic structure: chapters, sections, and labeled figures/tables.
2. Typeset every formula with math environments (e.g. `equation`, `align`) — never plain text.
3. Tables use `tabular`/`booktabs` and must stay within the page margins.
4. Reference figures, tables, and citations with `\ref`/`\cite` so links resolve.

## Hebrew-English (BiDi)

1. Assume a Unicode engine (LuaLaTeX/XeLaTeX) with explicit language switches.
2. Isolate right-to-left Hebrew runs from left-to-right English terms.
3. Keep English technical terms crisp inside Hebrew sentences; verify the transitions render.

## Boundaries

- You describe assembly intent and content; deterministic Python renders and compiles.
- Do not invent file paths; reference assets the harness will generate.
