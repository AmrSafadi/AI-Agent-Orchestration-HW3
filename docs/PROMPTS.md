# Prompt Engineering Log

Required by submission guideline 8.3. This log records the significant prompts
that drive the CrewAI agents and tasks, the design intent behind them, and
lessons applied. The authoritative prompt definitions live in
`src/bookgen/orchestration/agents.py` and `tasks.py`; this document explains and
inspects them.

## 1. Agent Prompts (role / goal / backstory)

Each agent is defined by a `role`, `goal`, and `backstory` (the system prompt),
following the CrewAI lecture pattern. Design rationale per agent is in
[AGENTS_DESIGN.md](../AGENTS_DESIGN.md).

| Agent | Role | Goal (summary) | Backstory intent |
|---|---|---|---|
| Planner | Document architect & compliance planner | Turn topic + requirements into a structured blueprint. | Senior technical editor; enforces a feature/acceptance checklist (max 3–5 chapters). |
| Research | Course-aligned research analyst | Collect/synthesize credible material and source candidates. | "Market research analyst" tuned to course concepts; proposes sources, never writes `.bib`. |
| Writer | Senior technical writer | Turn plan + research into clear prose. | Works *from context only* (no search tool); inserts placeholders for figures/table/formula/BiDi. |
| Reviewer | Senior editor & requirement reviewer | Improve clarity/accuracy without changing meaning; check coverage. | Editorial judgment; emits a requirement checklist and review report. |
| LaTeX | LaTeX assembly planner | Produce a `latex_spec.json` assembly intent. | Knows document structure; specifies but never compiles. |

## 2. Task Prompts (description / expected_output / context)

Tasks are chained by `context`, the reliable bridge between stages.

| Task | Description (intent) | Expected output | Context |
|---|---|---|---|
| Plan | Title, audience, chapter/section outline, feature placement, page budget, acceptance checklist. | `book_plan.json` (BookPlan schema). | — |
| Research | Key concepts, terminology, source candidates, per-chapter notes, unsupported-claim warnings. | `research_pack.json` (ResearchPack). | Plan |
| Write | Draft manuscript with citation markers and placeholders for image, graph, table, formula, Hebrew–English section. | `manuscript.md`. | Plan, Research |
| Review | Check clarity, consistency, assignment coverage; report approval, checklist, fixes. | `review_report.json` (ReviewReport). | Write |
| LaTeX spec | Template, chapter files, asset refs, bibliography file, output PDF path, engine, BiDi settings. | `latex_spec.json` (LatexSpec). | Review |

## 3. Prompt Design Principles Applied

- **Bounded roles.** Each prompt includes an explicit "not responsible for"
  scope to prevent role overlap (e.g., Writer does not search; LaTeX agent does
  not compile).
- **Structured outputs.** Every task names a target artifact and Pydantic schema
  so output can be validated, not just read.
- **Context over copying.** Downstream agents receive prior outputs via `context`
  rather than re-deriving them, mirroring the CrewAI "context is the glue" idea.
- **Determinism out of prompts.** Citations, graphs, validation, and compilation
  are removed from prompts and handled by the Python harness.

## 4. Lessons / Iteration Notes

- Splitting a single "write a book + make a PDF" prompt into five bounded agents
  removed source drift and made each step inspectable.
- Forcing each task to emit a schema-validated artifact caught structural gaps
  early (missing feature placements) before any rendering.
- Keeping the Writer tool-free (context-only) matched the lecture and reduced
  uncontrolled web content.

## 5. Real-Execution Note

These prompts are exercised against the model only under the opt-in
`--run-crew` path (Milestone 5). The default dry-run path validates the prompt
wiring without calling any API.
