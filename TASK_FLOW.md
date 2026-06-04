# TASK_FLOW.md

> **Status: historical.** This early planning document is superseded by the docs in `docs/` (see `docs/PROJECT_BLUEPRINT.md`, `docs/IMPLEMENTATION_STATUS.md`, `docs/ARCHITECTURE_DIAGRAM.md`). Kept for provenance.

## Why This Document Is Needed

This document shows how work moves through the system. It connects agents to tasks, tasks to context, and AI outputs to deterministic Python components.

CrewAI orchestration is not demonstrated by simply having agents. It is demonstrated by defining tasks, expected outputs, context dependencies, crew assembly, and process order.

## Course-Specific Basis

| Course source | Flow implication |
|---|---|
| CrewAI Part B pp. 2-10 | Build flow should be: define tools/components, define agents, define tasks, assemble crew, run kickoff. |
| L06 pp. 14-16 | Sequential process runs research -> writing -> review, with context passed between tasks. |
| CrewAI Part A p. 10 | `context` is the reliable bridge between task outputs. |
| L06 p. 17 | LaTeX/PDF production has required content and technical compilation steps. |
| L06 p. 18 | Final checking must verify technical details such as citations, BiDi, tables, formulas, and connected sections. |
| Feedback report pp. 2-4 | Quality, planning, configuration, cost awareness, and extensibility should be visible. |

## Detailed Draft

### Process Type

Version 1 uses:

```text
CrewAI Process: Sequential
```

Reason:

- The plan must exist before research.
- Research must exist before writing.
- Writing must exist before review.
- Reviewed content must exist before LaTeX assembly.
- LaTeX source must exist before PDF compilation.

Hierarchical process is a future extension only.

### Full Flow

```text
0. Load project configuration
1. Planner Task
2. Research Task
3. Writing Task
4. Review Task
5. LaTeX Assembly Task
6. Deterministic Citation Management
7. Deterministic Asset Generation
8. Deterministic Validation
9. Deterministic LaTeX Rendering
10. Deterministic PDF Compilation
11. Final Evidence Report
```

Only steps 1-5 are CrewAI agent tasks. Steps 6-11 are Python harness components.

## CrewAI Tasks

### Task 1: Plan The Article/Book

| Field | Value |
|---|---|
| Agent | Planner Agent |
| Context | None |
| Output | `book_plan.json` |

Expected output:

- Title and subtitle.
- Audience.
- Chapter outline.
- Section outline.
- Required feature placement.
- Page budget.
- Requirement checklist.

Course reason:

- The previous feedback asks for visible planning.
- The 2026 architecture handout emphasizes a Planner layer.

### Task 2: Research The Topic

| Field | Value |
|---|---|
| Agent | Research Agent |
| Context | `book_plan.json` |
| Output | `research_pack.json` |

Expected output:

- Key concepts.
- Course concept mapping.
- Source candidates.
- Chapter research notes.
- Terminology.
- Unsupported-claim warnings.

Course reason:

- Mirrors the Research Agent in the CrewAI lecture example.

### Task 3: Draft The Manuscript

| Field | Value |
|---|---|
| Agent | Writer Agent |
| Context | `book_plan.json`, `research_pack.json` |
| Output | `manuscript.md` or `manuscript.json` |

Expected output:

- Chapter prose.
- Sections.
- Citation markers.
- Placeholders for image, graph, table, and formula.
- Hebrew-English mixed section.
- Captions.

Course reason:

- Mirrors the lecture's Writer Agent that works from research context rather than using its own search tool.

### Task 4: Review And Polish

| Field | Value |
|---|---|
| Agent | Reviewer Agent |
| Context | `book_plan.json`, `research_pack.json`, `manuscript` |
| Output | `reviewed_manuscript`, `review_report.json` |

Expected output:

- Polished manuscript.
- Requirement checklist.
- Editorial notes.
- Source/citation concerns.
- Missing feature warnings.

Course reason:

- Mirrors the lecture's Senior Editor / Quality Reviewer role.

### Task 5: Create LaTeX Assembly Specification

| Field | Value |
|---|---|
| Agent | LaTeX Agent |
| Context | `book_plan.json`, `reviewed_manuscript`, `review_report.json` |
| Output | `latex_spec.json` |

Expected output:

- Cover metadata mapping.
- Chapter-to-template mapping.
- Figure/table/formula placement.
- Citation placement requests.
- BiDi section metadata.
- Asset references.

Course reason:

- L06 p. 17 requires LaTeX PDF production, but the course also emphasizes guardrails. Therefore, the agent prepares assembly intent while Python renders and compiles.

## Deterministic Harness Steps

### Step 6: Citation Management

Component:

`CitationManager`

Inputs:

- `research_pack.json`
- `reviewed_manuscript`
- curated source registry

Outputs:

- `references.bib`
- `citation_report.json`

Checks:

- Every citation marker maps to a known source.
- Every cited source appears in `.bib`.
- No invalid citation keys.
- No fabricated bibliography entries.

### Step 7: Asset Generation

Component:

`AssetGenerator`

Inputs:

- `latex_spec.json`
- `book_plan.json`

Outputs:

- Python-generated graph.
- Image asset references.
- Table data.
- Formula metadata.

Required graph:

- A Python-generated graph showing the sequential agent/document pipeline.

### Step 8: Validation

Component:

`DocumentValidator`

Inputs:

- all previous artifacts

Outputs:

- `validation_report.json`

Checks:

- Cover page data exists.
- TOC enabled.
- Chapters and sections exist.
- At least one image exists.
- Python graph exists.
- Table exists.
- Formula exists as display math.
- Hebrew-English section exists.
- `.bib` file exists.
- Citation keys resolve.
- LaTeX spec references valid files.

### Step 9: LaTeX Rendering

Component:

`LatexRenderer`

Inputs:

- `latex_spec.json`
- `reviewed_manuscript`
- `references.bib`
- generated assets

Outputs:

- `main.tex`
- chapter `.tex` files
- copied assets
- final `.bib`

Rendering policy:

- Use templates.
- Escape unsafe text.
- Keep Hebrew-English handling explicit.
- Use LuaLaTeX-compatible packages first; XeLaTeX-compatible fallback second.

### Step 10: PDF Compilation

Component:

`PDFCompiler`

Inputs:

- generated LaTeX project

Outputs:

- `final.pdf`
- `build.log`

Recommended sequence:

```text
lualatex -> biber/bibtex -> lualatex -> lualatex
```

This follows the lecture note that references and citations may require multiple compilation passes.

### Step 11: Final Evidence Report

Component:

`EvidenceReporter`

Outputs:

- `final_report.md`

Contents:

- Generated PDF path.
- Requirement checklist.
- Agent task outputs.
- Validation status.
- Build status.
- Cost/token summary if available.
- Known limitations.

## Requirement Coverage Matrix

| Requirement | CrewAI task | Deterministic component |
|---|---|---|
| Multiple specialized agents | Tasks 1-5 | None |
| CrewAI orchestration | Tasks 1-5 | None |
| Sequential process | Crew setup | None |
| Cover page | Planner, LaTeX Agent | Renderer |
| Table of contents | Planner, LaTeX Agent | Renderer |
| Chapters and sections | Planner, Writer, Reviewer | Validator, Renderer |
| Bibliography and citations | Research, Writer, Reviewer | CitationManager, Renderer, Compiler |
| Images | Planner, Writer, LaTeX Agent | AssetGenerator, Validator |
| Python-generated graph | Planner, LaTeX Agent | AssetGenerator |
| Mathematical formula | Writer, Reviewer, LaTeX Agent | Validator, Renderer |
| Table | Writer, Reviewer, LaTeX Agent | Validator, Renderer |
| Hebrew-English mixed section | Writer, Reviewer, LaTeX Agent | Validator, Renderer, Compiler |
| Final PDF output | LaTeX Agent | Renderer, PDFCompiler |

## Alternatives

| Alternative | Benefit | Risk |
|---|---|---|
| Add revision loop after review | Better content quality. | Sequential v1 becomes more complex. |
| Compile before review | Reviewer could inspect final PDF. | Technical errors happen before editorial issues are resolved. |
| Research and planning in parallel | Faster. | Planner output is needed to focus research. |
| Citation handling inside Research Agent | Fewer components. | More hallucination and invalid BibTeX risk. |

## Risks

| Risk | Mitigation |
|---|---|
| Agent output does not match expected schema. | Validate after each task. |
| Review discovers major gaps late. | Planner includes acceptance checklist from the first task. |
| Deterministic validator blocks compilation. | Keep validation messages actionable and save all artifacts. |
| Bibliography fails during build. | CitationManager writes `.bib` before rendering and compiler logs are preserved. |
| Generated PDF misses a course requirement. | Requirement matrix is checked by Validator and EvidenceReporter. |

