# PROJECT_PLAN.md

> **Status: historical.** This early planning document is superseded by the docs in `docs/` (see `docs/PROJECT_BLUEPRINT.md`, `docs/IMPLEMENTATION_STATUS.md`, `docs/ARCHITECTURE_DIAGRAM.md`). Kept for provenance.

## Why This Document Is Needed

This document defines the homework goal, scope, course alignment, deliverables, acceptance criteria, and implementation phases before any code is written.

It directly addresses the previous feedback report, which identified missing foundational planning documentation as an improvement area. It also follows the software submission guidelines, which require a project-level plan, clear requirements, setup expectations, and evidence that design decisions were made before implementation.

## Course-Specific Observations

### Concepts Emphasized By The Lecturer

The plan is based on these course signals:

| Course source | Observation | Design consequence |
|---|---|---|
| `main-L06-summary-and-ex03-defination.pdf`, pp. 13-16 | CrewAI is taught through Agent, Task, Crew, and Process. Context links the output of one task to the next. | The system must explicitly model these four concepts and show task context dependencies. |
| `CrewAI Part A`, pp. 3-10 | The lecturer presents CrewAI as a team of agents working like an organization, not one long prompt. | Use a small specialized team with clear roles, not a single document-generation prompt. |
| `CrewAI Part A`, pp. 7-8 | Sequential and Hierarchical processes are compared. Sequential waits for previous task output; Hierarchical uses a manager. | Version 1 uses `Process.sequential`; hierarchical orchestration is reserved for a future version. |
| `CrewAI Part B`, pp. 2-11 | The lecturer walks from pseudocode to a complete crew: define tools, define agents, define tasks, assemble crew, run `kickoff`. | The implementation plan follows that order and preserves visible intermediate outputs. |
| `LangChain_...pdf`, pp. 2-5, 10, 14-15 | The lecturer emphasizes the "Harness": model plus prompt, tools, context, memory, parser/output, modularity, testing, observability, and guardrails. | The project wraps CrewAI in a deterministic harness: config, schemas, validators, asset generation, citation management, and PDF build steps. |
| `AI Agent Architecture 2026`, pp. 3, 8-15 | Modern agent systems are described through runtime layers, RAG/state/types/teams, governance, observability, security, and TCO. | Keep v1 small but production-shaped: structured artifacts, validation, logs, cost awareness, and future extension points. |
| `main-v4-Agents-Subagents-Commands.pdf`, pp. 4-5 | Skills/tools should move heavy deterministic work out of prompts. | Citation reconciliation, graph creation, validation, and PDF compilation are Python components, not agents. |
| `main-L06-summary-and-ex03-defination.pdf`, p. 17 | The assignment requires an article/book PDF with LaTeX, cover sheet, TOC, sections, images, Python graph, table, formula, Hebrew-English BiDi, bibliography, and repeated compilation. | These become hard acceptance criteria. LuaLaTeX is preferred because the lecture recommends it for Hebrew support; XeLaTeX remains fallback. |
| `software_submission_guidelines-V3.pdf`, pp. 7-9 | Required engineering hygiene includes README, docs, PLAN, TODO, modular folder structure, config, tests, `.env-example`, and `.gitignore`. | The project plan includes docs, config, generated outputs, tests, and secret handling from day one. |
| `Detailed_Feedback_Report_252593.pdf`, pp. 2-4 | The previous feedback rewarded documentation, testing, research analysis, UX, version management, and asked for better planning, config/security, cost awareness, extensibility, and quality standards. | The project must show planning, deterministic validation, cost notes, versioned config, and quality gates, not just a generated PDF. |

### Technologies Explicitly Taught Or Mentioned

The course material explicitly mentions or demonstrates:

- CrewAI: `Agent`, `Task`, `Crew`, `Process`, `Process.sequential`, `Process.hierarchical`, `context`, `verbose`, `kickoff`.
- LangChain and LCEL: modular harness thinking, retrievers, prompt templates, parsers, model providers.
- LangGraph: stateful graph orchestration, planner/tool-call/retry/human-review loops.
- RAG, embeddings, vector stores, retrievers.
- Tools, Skills, MCP, A2A.
- Python automation.
- LaTeX, LuaLaTeX, XeLaTeX, MiKTeX, BibTeX/biber, TikZ.
- Sandbox/WSL and security risks such as prompt injection and memory poisoning.
- Observability, testing, guardrails, versioning, cost/TCO awareness.

Version 1 intentionally uses only the technologies required for the assignment: Python, CrewAI, LaTeX/LuaLaTeX, BibTeX/biber, and deterministic Python components.

## Detailed Draft

### Project Title

CrewAI Article/Book Generator With Professional LaTeX PDF Output

### Goal

Build a small, well-engineered multi-agent system using CrewAI that generates a professional article or short book and produces a final PDF using LaTeX.

The project must demonstrate the course philosophy: transform a single broad prompt into an organized team of agents, pass task outputs through explicit context, and surround the AI steps with deterministic engineering components that make the output reliable.

### Recommended Topic

Recommended topic for v1:

`Football Analytics and AI-Based Match Strategy`

This topic gives the PDF an independent subject while the codebase still demonstrates the lecture requirements: CrewAI orchestration, deterministic harnessing, validation, LaTeX production, observability, and submission-grade engineering hygiene.

### Agent Set

Use exactly five CrewAI agents:

1. Planner Agent
2. Research Agent
3. Writer Agent
4. Reviewer Agent
5. LaTeX Agent

No Citation Agent, Visuals Agent, QA Agent, or Manager Agent in v1.

### Deterministic Python Components

These responsibilities must remain deterministic Python components:

- Citation management and bibliography reconciliation.
- Python graph generation.
- Schema and requirement validation.
- LaTeX escaping and template rendering support.
- PDF compilation.
- Build log capture.
- Cost/token summary if model providers expose usage.

This follows the course distinction between agents as reasoning workers and tools/skills/components as reliable execution mechanisms.

### In Scope

- Sequential CrewAI process.
- Five specialized agents.
- Structured intermediate artifacts.
- Professional article/book PDF.
- Cover page.
- Table of contents.
- Chapters and sections.
- Headers/footers.
- Bibliography and citations.
- At least one image.
- One Python-generated graph.
- One mathematical formula rendered as a real display equation.
- One table.
- One Hebrew-English mixed text section demonstrating BiDi.
- Final PDF output.
- Validation report.
- Build logs.
- Documentation and engineering plan.

### Out Of Scope For Version 1

- Hierarchical CrewAI manager process.
- LangGraph implementation.
- Full RAG vector database.
- MCP/A2A server integration.
- Web application.
- Human-in-the-loop editing UI.
- Complex autonomous web crawling.
- Multi-book publishing workflow.

These topics may be mentioned as future work because the course teaches them, but including them in v1 would make the system too large for a focused homework.

### Success Criteria

The project is successful if:

| Requirement | Acceptance criterion |
|---|---|
| CrewAI orchestration | The implementation defines `Agent`, `Task`, `Crew`, and `Process.sequential`. |
| Specialized agents | The five required agents have distinct roles, goals, backstories, and expected outputs. |
| Context flow | Each task after planning receives explicit context from previous tasks. |
| Professional PDF | The final PDF compiles successfully and looks like a polished article/book. |
| LaTeX features | Cover page, TOC, chapters, sections, headers/footers, table, formula, images, graph, citations, and bibliography are present. |
| Hebrew-English section | A BiDi section renders correctly with Hebrew and English on the same page. |
| Deterministic components | Citation management, graph generation, validation, and PDF compilation are Python-driven, not prompt-driven. |
| Engineering quality | Docs, config, tests, logs, and generated outputs are organized according to the course software guidelines. |
| Demonstrability | A grader can inspect intermediate files and understand how the agents collaborated. |

### Implementation Phases

| Phase | Purpose | Deliverables |
|---|---|---|
| 0. Planning | Align architecture with course material before coding. | These five planning documents. |
| 1. Skeleton | Prepare directories, config, dependencies, and templates. | Empty package structure, config files, `.env-example`, LaTeX templates. |
| 2. Schemas | Define structured intermediate artifacts. | Document plan schema, research pack schema, manuscript schema, LaTeX spec schema. |
| 3. CrewAI definitions | Define agents, tasks, and sequential crew. | Agent/task/crew modules. |
| 4. Deterministic components | Add citation manager, graph generator, validators, renderer, compiler. | Python services with unit tests. |
| 5. End-to-end run | Generate one complete article/book. | Intermediate JSON/Markdown artifacts, LaTeX source, PDF. |
| 6. Quality pass | Validate all requirements and polish documentation. | Validation report, build logs, final README updates. |

### Course-Aligned Design Decisions

| Decision | Reason | Course reference |
|---|---|---|
| Use five agents only. | The lecturer's CrewAI examples favor clear roles over agent sprawl. | CrewAI Part A pp. 3-6; L06 pp. 13-16. |
| Use sequential process in v1. | The document pipeline has hard dependencies: plan before research, research before writing, writing before review, review before LaTeX. | CrewAI Part A pp. 7-8; L06 p. 14. |
| Keep citation management deterministic. | Source and bibliography correctness should be validated, not improvised. | L06 p. 17; feedback report pp. 2-4. |
| Keep graph generation deterministic. | The assignment requires a Python-generated graph; Python should produce the graph directly. | L06 p. 17. |
| Prefer LuaLaTeX. | The lecture recommends LuaLaTeX for Hebrew support and allows XeLaTeX. | L06 p. 17. |
| Use structured artifacts. | Context passing is central in CrewAI; structured files make the context inspectable and debuggable. | CrewAI Part A p. 10; Part B pp. 6-9. |
| Add validators. | The lecture and feedback both emphasize guardrails, testing, and quality standards. | LangChain slides p. 15; feedback report pp. 3-4. |
| Document cost awareness. | Prior feedback explicitly called out missing cost/resource awareness. | Feedback report p. 4; AI Architecture 2026 p. 14. |

## Alternatives

| Alternative | Benefit | Why not v1 |
|---|---|---|
| Hierarchical CrewAI process with Manager Agent | Stronger demonstration of advanced CrewAI orchestration. | User requested sequential v1; hierarchical is better after the pipeline is stable. |
| LangGraph instead of CrewAI | Better for loops, retries, state machines, and human review. | Assignment specifically asks for CrewAI. |
| Full RAG with vector store | Aligns with course RAG material. | Adds complexity not required for the PDF assignment. |
| Let LaTeX Agent write all `.tex` directly | Looks agentic and simple. | Fragile; malformed LaTeX could break compilation. Templates plus validation are safer. |
| Add Citation Agent and Visuals Agent | More agents on paper. | User explicitly restricted the agent list; deterministic components are more reliable. |

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Agent outputs invalid structure | Later tasks fail. | Require JSON/Markdown schemas and validation after each stage. |
| Hallucinated citations | Bibliography becomes untrustworthy. | Use a curated source registry and deterministic citation manager. |
| LaTeX compilation failure | No final PDF. | Use templates, escaping utilities, validation, and logged multi-pass compilation. |
| Hebrew-English rendering issues | BiDi requirement fails. | Prefer LuaLaTeX, use proper language/font packages, and validate the generated section. |
| Project becomes too complex | Hard to finish and explain. | Keep v1 sequential with five agents and deterministic components. |
| Cost grows through repeated agent calls | Harder to run and grade. | Limit task count, cache intermediate outputs, and log usage/cost. |
| Grader cannot see the orchestration | Good output but weak demonstration. | Persist intermediate artifacts and verbose CrewAI logs. |

