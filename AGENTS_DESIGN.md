# AGENTS_DESIGN.md

> **Status: historical.** This early planning document is superseded by the docs in `docs/` (see `docs/PROJECT_BLUEPRINT.md`, `docs/IMPLEMENTATION_STATUS.md`, `docs/ARCHITECTURE_DIAGRAM.md`). Kept for provenance.

## Why This Document Is Needed

This document defines the five allowed agents and prevents role overlap. It makes the "agent team as an organization" idea concrete and keeps the system small enough to explain in a university presentation.

The design follows the CrewAI lecture pattern: every agent has a role, goal, backstory, optional tools, and task-specific expected outputs.

## Course-Specific Basis

| Course idea | How it shapes this design |
|---|---|
| Agent = role, goal, backstory, tools (L06 p. 13; CrewAI Part A p. 4). | Each agent has these fields documented before implementation. |
| Writer in the lecture works from context, not from a search tool (L06 p. 15). | Only the Research Agent may use external source tools in v1; Writer works from Planner/Research context. |
| Review Agent checks accuracy, clarity, and structure (CrewAI Part B p. 8; L06 p. 15). | Reviewer Agent validates content and requirement coverage, while deterministic validators check technical build readiness. |
| Context bridges tasks (CrewAI Part A p. 10). | Every agent after Planner consumes previous artifacts explicitly. |
| Skills/tools should move deterministic work out of prompts (`main-v4`, pp. 4-5). | Citation management, graph generation, validation, and PDF compilation are not agents. |

## Detailed Draft

### Agent Overview

| Agent | Main responsibility | Main output |
|---|---|---|
| Planner Agent | Defines document intent, structure, feature placement, and acceptance checklist. | `book_plan.json` |
| Research Agent | Produces course-aligned research material and source candidates. | `research_pack.json` |
| Writer Agent | Writes the article/book manuscript from plan and research context. | `manuscript.md` or `manuscript.json` |
| Reviewer Agent | Reviews and polishes content while preserving meaning and checking requirements. | `reviewed_manuscript` and `review_report.json` |
| LaTeX Agent | Creates a LaTeX assembly specification for deterministic rendering. | `latex_spec.json` |

## 1. Planner Agent

### Role

Document architect and assignment compliance planner.

### Goal

Transform the user topic and course requirements into a clear article/book blueprint.

### Backstory

The Planner Agent behaves like a senior technical editor who understands the lecturer's emphasis on structured workflows, clear task outputs, and professional deliverables.

### Tools

None required in v1.

### Inputs

- User topic.
- Assignment requirements.
- Course-specific design constraints.
- Target length and audience.

### Outputs

`book_plan.json` containing:

- Proposed title and subtitle.
- Target audience.
- Chapter outline.
- Section outline.
- Placement plan for image, graph, table, formula, citations, and Hebrew-English section.
- Acceptance checklist.
- Estimated page budget.

### Not Responsible For

- Writing full prose.
- Managing citations.
- Rendering LaTeX.
- Generating graph files.

### Design Decision

This agent exists because the 2026 architecture slides emphasize a Planner runtime layer, and the previous feedback explicitly asked for better planning. It also keeps the later Writer Agent from inventing structure midstream.

### Risks

- May over-plan too many chapters.
- May forget a required PDF element.

### Mitigation

The expected output must include a requirement coverage checklist and a maximum of 3-5 chapters.

## 2. Research Agent

### Role

Course-aligned research analyst.

### Goal

Collect and synthesize credible material for the chosen topic.

### Backstory

The Research Agent acts like the "Market Research Analyst" from the CrewAI lecture example, but tuned for this course: it must connect content to Agent, Task, Crew, Process, harnesses, modularity, observability, security, and LaTeX production.

### Tools

Optional in v1:

- Search tool if available.
- Local course notes or curated source registry.

The Research Agent does not directly write `.bib` files. It only proposes source candidates and source summaries.

### Inputs

- `book_plan.json`.
- Topic.
- Curated source list if available.

### Outputs

`research_pack.json` containing:

- Key concepts.
- Definitions.
- Course-aligned observations.
- Suggested citations using provisional source IDs.
- Notes for each chapter.
- Warnings about unsupported claims.

### Not Responsible For

- Final bibliography generation.
- Citation key validation.
- PDF generation.

### Design Decision

The lecture examples put search/research responsibility in a dedicated research agent, while the Writer works from context. This separation directly mirrors L06 pp. 14-15 and CrewAI Part B pp. 2-3.

### Risks

- Hallucinated or weak sources.
- Too much broad background.

### Mitigation

Use a deterministic Citation Manager later. Research output is advisory until validated.

## 3. Writer Agent

### Role

Senior technical writer.

### Goal

Turn the plan and research pack into a clear professional manuscript.

### Backstory

The Writer Agent mirrors the lecture's "Senior Technical Writer": it transforms raw research into accessible prose and does not search independently.

### Tools

None in v1.

### Inputs

- `book_plan.json`.
- `research_pack.json`.

### Outputs

`manuscript.md` or `manuscript.json` containing:

- Cover metadata text.
- Chapter content.
- Section content.
- Citation markers using approved placeholder IDs.
- Figure/image placeholders.
- Graph placement.
- Table placement.
- Formula placement.
- Hebrew-English mixed section.

### Not Responsible For

- Verifying final citations.
- Producing actual graph files.
- Producing final `.tex`.
- Compiling PDF.

### Design Decision

The Writer Agent works from context because the CrewAI lecture explicitly shows the writing agent with no search tool and a context dependency on the research task. This makes the orchestration visible and reduces uncontrolled source drift.

### Risks

- Prose may be generic.
- Citation markers may not match final bibliography.
- Hebrew-English section may be linguistically awkward.

### Mitigation

Reviewer Agent checks prose and requirements; Citation Manager validates citation keys; LaTeX rendering validates BiDi behavior.

## 4. Reviewer Agent

### Role

Senior editor and requirement reviewer.

### Goal

Review the manuscript for accuracy, clarity, flow, course alignment, and assignment coverage.

### Backstory

The Reviewer Agent follows the lecture's review agent pattern: improve clarity and factual accuracy without changing the original meaning. It also incorporates the previous feedback's engineering mindset: requirements must be visibly checked.

### Tools

None in v1.

### Inputs

- `book_plan.json`.
- `research_pack.json`.
- `manuscript`.

### Outputs

- `reviewed_manuscript`.
- `review_report.json`.

The review report should include:

- Requirement checklist.
- Content-quality notes.
- Unsupported claim warnings.
- Missing element warnings.
- Suggested fixes already applied or still required.

### Not Responsible For

- Running deterministic validation.
- Compiling PDF.
- Generating `.bib`.

### Design Decision

The Reviewer Agent is kept as an agent because editorial review is judgment-heavy. Technical validation remains deterministic because the lecturer's summary warns that the final check is technical, not only content-based.

### Risks

- Reviewer may approve incomplete content.
- Reviewer may rewrite too aggressively.

### Mitigation

Give the Reviewer a strict checklist from Planner output and require a separate deterministic validation report later.

## 5. LaTeX Agent

### Role

LaTeX assembly planner.

### Goal

Convert the reviewed manuscript into a structured LaTeX assembly specification that deterministic Python rendering can safely compile.

### Backstory

The LaTeX Agent understands professional document structure and the assignment's LaTeX requirements, but it does not directly run compilers or own build correctness.

### Tools

None in v1.

### Inputs

- `reviewed_manuscript`.
- `book_plan.json`.
- `review_report.json`.
- Known template capabilities.

### Outputs

`latex_spec.json` containing:

- Document class intent.
- Chapter-to-template mapping.
- Cover page fields.
- TOC requirement.
- Header/footer metadata.
- Figure/table/formula placement.
- BiDi section metadata.
- Citation marker mapping requests.
- Asset file references.

### Not Responsible For

- Final citation reconciliation.
- Actual graph/image generation.
- LaTeX escaping.
- PDF compilation.
- Build validation.

### Design Decision

This preserves a LaTeX Agent while respecting the course's production-harness idea. The agent decides document assembly intent; deterministic Python handles fragile syntax, escaping, bibliography files, and compiler execution.

### Risks

- Agent may request unsupported template features.
- Agent may create invalid asset references.

### Mitigation

Validator checks `latex_spec.json` against known templates and generated assets.

## Excluded Agents

These are intentionally not used in v1:

| Excluded agent | Why excluded |
|---|---|
| Citation Agent | User requested deterministic citation management. |
| Visuals Agent | Graph generation and asset validation should be deterministic. |
| QA Agent | Reviewer Agent covers editorial review; deterministic validators cover technical QA. |
| Manager Agent | User requested sequential CrewAI process for v1. |
| Translator Agent | Hebrew-English section is a manuscript requirement handled by Writer and checked by Reviewer/validator. |

## Alternatives

| Alternative | Benefit | Why not chosen |
|---|---|---|
| Three-agent crew: Research, Writer, Reviewer | Matches the lecture pseudocode exactly. | The assignment also needs planning and LaTeX-specific assembly. |
| Seven-agent crew | More specialized. | Violates the user's requested agent list and increases fragility. |
| Manager Agent | Stronger hierarchy demonstration. | Reserved for future v2; v1 must be sequential. |
| Tool-heavy Research Agent | Could automate source retrieval. | Citation correctness is more important than autonomous breadth for this homework. |

## Risks

| Risk | Mitigation |
|---|---|
| Agents overlap responsibilities. | Keep "Not Responsible For" sections in prompts and docs. |
| Agents output prose instead of structured artifacts. | Define expected output schemas per task. |
| LaTeX Agent becomes a hidden compiler. | Restrict it to assembly specification only. |
| Reviewer misses technical problems. | Use deterministic validation after the crew completes. |

