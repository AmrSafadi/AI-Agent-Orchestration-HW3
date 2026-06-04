# ARCHITECTURE.md

> **Status: historical.** This early planning document is superseded by the docs in `docs/` (see `docs/PROJECT_BLUEPRINT.md`, `docs/IMPLEMENTATION_STATUS.md`, `docs/ARCHITECTURE_DIAGRAM.md`). Kept for provenance.

## Why This Document Is Needed

This document explains how the system is structured before implementation. It maps the lecturer's CrewAI concepts - Agent, Task, Crew, and Process - to concrete project components.

It also responds to the software guidelines and previous feedback by making architecture, trade-offs, validation, configuration, cost awareness, and extensibility visible before code exists.

## Course-Specific Basis

The architecture follows these course ideas:

- CrewAI is an "agent team as an organization" rather than one long prompt (`CrewAI Part A`, pp. 2-6; L06 p. 13).
- `Agent` means role, goal, backstory, and tools; `Task` means description and expected output; `Crew` connects agents and tasks; `Process` controls execution order (L06 pp. 13-14).
- `context` is the bridge from one task output to the next (`CrewAI Part A`, p. 10; `CrewAI Part B`, pp. 6-9).
- Sequential process is appropriate when each task depends on the previous result (`CrewAI Part A`, p. 7; L06 p. 14).
- A production-like "Harness" should wrap model calls with tools, context, parsing, validation, observability, and guardrails (`LangChain_...pdf`, pp. 2-5, 10, 14-15).
- The assignment's LaTeX PDF must include complex document features and requires multiple compilation passes when `.tex` and `.bib` files are involved (L06 p. 17).
- The 2026 architecture handout emphasizes runtime layers, governance, RAG/state/team choices, observability, security, and TCO (`AI Agent Architecture 2026`, pp. 3, 8-15).

## Detailed Draft

### Architecture Style

Use a sequential pipeline architecture wrapped in a deterministic engineering harness.

The AI agents produce structured intellectual work:

- planning,
- research synthesis,
- writing,
- review,
- LaTeX assembly intent.

Python components perform fragile or verifiable work:

- citation reconciliation,
- graph generation,
- validation,
- LaTeX rendering support,
- PDF compilation.

### High-Level Diagram

```text
------------------+
| Project Config  |
| topic, author,  |
| model, budget,  |
| PDF settings    |
+--------+---------+
         |
         v
+--------------------------+
| CrewAI Sequential Crew   |
|                          |
| 1. Planner Agent         |
| 2. Research Agent        |
| 3. Writer Agent          |
| 4. Reviewer Agent        |
| 5. LaTeX Agent           |
+------------+-------------+
             |
             v
+--------------------------+
| Structured Artifacts     |
| plan, research pack,     |
| manuscript, review,      |
| latex assembly spec      |
+------------+-------------+
             |
             v
+--------------------------+
| Deterministic Harness    |
| citation manager         |
| graph generator          |
| image/table/formula prep |
| validators               |
| latex renderer           |
| PDF compiler             |
+------------+-------------+
             |
             v
+--------------------------+
| Generated LaTeX + PDF    |
| main.tex, chapters, bib, |
| assets, final.pdf, logs  |
+--------------------------+
```

### Mapping To CrewAI Concepts

| CrewAI concept | Project interpretation |
|---|---|
| Agent | A specialized worker with role, goal, backstory, and possibly tools. Only five agents are used. |
| Task | A measurable unit of work with description, expected output, assigned agent, and context dependencies. |
| Crew | The ordered team that executes the five agent tasks. |
| Process | `Process.sequential` for v1 because outputs must flow in order. |

### Runtime Components

#### 1. Configuration Layer

Purpose:

- Define topic, title, author, course name, lecturer name, output paths, model provider, token budget, and PDF engine.
- Keep secrets outside source control through `.env` and `.env-example`.

Course reason:

- The software guidelines require configuration hygiene, `.env-example`, and no hardcoded secrets.
- The previous feedback called out configuration and security portability.

#### 2. Crew Orchestration Layer

Purpose:

- Create the five agents.
- Create the five CrewAI tasks.
- Link task context explicitly.
- Run the crew with `Process.sequential`.
- Save verbose logs and outputs.

Course reason:

- This directly follows the "from pseudocode to full workflow" structure in CrewAI Part B.

#### 3. Document Artifact Layer

Purpose:

- Store each stage output in inspectable files.
- Avoid passing only unstructured text.

Recommended artifacts:

| Artifact | Produced by | Purpose |
|---|---|---|
| `book_plan.json` | Planner Agent | Title, audience, chapter outline, required feature placement. |
| `research_pack.json` | Research Agent | Source summaries, course concepts, source candidates, terminology. |
| `manuscript.md` or `manuscript.json` | Writer Agent | Draft chapters and sections in a safe intermediate format. |
| `review_report.json` | Reviewer Agent | Checklist review and approved manuscript corrections. |
| `latex_spec.json` | LaTeX Agent | Mapping from manuscript elements to LaTeX template slots. |
| `citation_registry.json` | Citation Manager | Valid citation keys and source metadata. |
| `validation_report.json` | Validator | Requirement coverage and build readiness. |

Course reason:

- Context is a first-class concept in the CrewAI lectures. Persisting artifacts makes the context chain visible to the grader.

#### 4. Deterministic Citation Manager

Purpose:

- Maintain a curated bibliography source registry.
- Match citation markers to known keys.
- Generate `references.bib`.
- Report uncited sources, missing keys, and malformed entries.

Why deterministic:

- Citations are graded artifacts and should not depend on a model improvising BibTeX syntax.

#### 5. Deterministic Graph Generator

Purpose:

- Generate one Python graph as required by the assignment.

Recommended graph:

`agent_pipeline_graph.png`: a pipeline visualization showing Planner -> Research -> Writer -> Reviewer -> LaTeX -> deterministic build components.

Why deterministic:

- The lecture requires a Python-generated graph. A deterministic graph is reproducible and easy to validate.

#### 6. Deterministic Validator

Purpose:

- Check that all required elements exist before compilation.

Validation checklist:

- Cover metadata exists.
- TOC enabled.
- Chapters and sections exist.
- At least one image exists.
- Python graph file exists.
- Table exists.
- Display formula exists and is not plain text.
- Hebrew-English BiDi section exists.
- Citation keys are valid.
- `.bib` file exists.
- LaTeX source files exist.

Course reason:

- L06 p. 18 says the check is technical, not only content-level: connected sections, citations, BiDi, tables, and formulas must work.
- LangChain slides emphasize testing, observability, and guardrails.

#### 7. LaTeX Rendering And PDF Build Layer

Purpose:

- Render final `.tex` files using templates.
- Compile PDF.
- Capture build logs.

Recommended engine:

- Default: LuaLaTeX, because L06 p. 17 recommends it for Hebrew support.
- Fallback: XeLaTeX, because L06 p. 17 allows it.

Recommended build sequence:

- `lualatex`
- `biber` or `bibtex`
- `lualatex`
- `lualatex`

Or use `latexmk` configured for LuaLaTeX.

### Data Flow

```text
project_config
  -> planning_task
  -> book_plan.json
  -> research_task
  -> research_pack.json
  -> writing_task
  -> manuscript
  -> review_task
  -> reviewed_manuscript + review_report
  -> latex_task
  -> latex_spec.json
  -> citation_manager
  -> graph_generator
  -> validators
  -> latex_renderer
  -> pdf_compiler
  -> final.pdf
```

### Quality Gates

Before final submission, the project should provide:

| Gate | Reason |
|---|---|
| Schema validation | Prevent invalid agent outputs from cascading. |
| Citation validation | Prevent hallucinated or missing bibliography entries. |
| Asset validation | Ensure graph/images/tables/formula assets exist. |
| LaTeX validation | Catch missing files and unsafe characters before compilation. |
| PDF compilation status | Prove final artifact exists. |
| Cost summary | Address previous feedback on costs and pricing. |
| Test report | Align with software guidelines and quality standards. |

## Alternatives

| Alternative | Benefit | Risk |
|---|---|---|
| Direct agent-generated LaTeX | Fast to implement. | High chance of compile errors and broken BiDi/citations. |
| Markdown -> Pandoc -> PDF | Simple content flow. | Hides LaTeX details and may weaken demonstration of LaTeX requirements. |
| Hierarchical CrewAI | Demonstrates manager-agent orchestration. | More complexity than v1 needs; user requested sequential. |
| LangGraph | Strong state/retry control. | Not the required framework for this homework. |
| Full RAG source retrieval | More advanced and course-aligned. | Unnecessary complexity for a focused PDF generation assignment. |

## Risks

| Risk | Mitigation |
|---|---|
| Sequential pipeline has no automatic revision loop. | Let Reviewer produce a polished manuscript in v1; add loops in v2. |
| Agent output is too long or inconsistent. | Limit chapters and require structured outputs. |
| LaTeX Agent produces unsafe TeX fragments. | Use templates and escaping; keep renderer deterministic. |
| Hebrew fonts unavailable. | Document required fonts and provide LuaLaTeX/XeLaTeX fallback. |
| Bibliography mismatch. | Restrict citations to a curated source registry. |
| Overengineering. | Keep five agents and one pipeline; put advanced features in future work. |

