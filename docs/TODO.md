# Task Tracking (TODO)

Mandatory document per submission guideline 2.2. This is the detailed,
granular task backlog (550+ tasks) for the project, grouped by phase. It
complements `docs/IMPLEMENTATION_STATUS.md` (milestone evidence) and the
higher-level plan in `docs/PROJECT_BLUEPRINT.md`.

Status legend: `[x]` Completed · `[ ]` Not started / in progress. Each task
has a stable id `T###` for cross-referencing in commits and reviews.

## Phase A — Foundations

### A. Repository & Tooling

- [x] **T001** Initialize git repository and default branch
- [x] **T002** Create `pyproject.toml` as the single dependency source (no requirements.txt)
- [x] **T003** Adopt `uv` as the only package manager and task runner
- [x] **T004** Add `.gitignore` for `.env`, `generated/`, `data/references/`, caches
- [x] **T005** Add `.env-example` with dummy values (single guideline-named file)
- [x] **T006** Create `src/bookgen/` package layout with subpackages
- [x] **T007** Add `README.md` with install/run/test commands
- [x] **T008** Add planning docs: PROJECT_PLAN, ARCHITECTURE, AGENTS_DESIGN, TASK_FLOW, FOLDER_STRUCTURE
- [x] **T009** Centralize the package version in `shared/version.py`
- [x] **T010** Wire `bookgen.__init__` to re-export `__version__`

### B. Configuration

- [x] **T011** Create `config/setup.json` with project metadata and workflow
- [x] **T012** Create `config/models.json` with provider/model defaults
- [x] **T013** Create `config/latex.json` with engine (lualatex/xelatex/biber)
- [x] **T014** Create `config/budgets.json` with cost placeholders
- [x] **T015** Implement `shared/config.py` Pydantic loaders
- [x] **T016** Validate the approved five-agent set in config
- [x] **T017** Add a version key to each versioned config file (`setup`/`models`/`latex`/`budgets` all carry one, validated by Pydantic)
- [x] **T018** Add config-loading unit tests
- [x] **T019** Audit configs for hardcoded values that belong in config
- [x] **T020** Implement `shared/logging.py` logging setup

## Phase B — Schemas

### C. Pydantic Artifact Contracts

- [x] **T021** Schema — BookPlan: define fields and types.
- [x] **T022** Schema — BookPlan: add field validators.
- [x] **T023** Schema — BookPlan: document an example payload.
- [x] **T024** Schema — BookPlan: add a round-trip serialization test.
- [x] **T025** Schema — ResearchPack: define fields and types.
- [x] **T026** Schema — ResearchPack: add field validators.
- [x] **T027** Schema — ResearchPack: document an example payload.
- [x] **T028** Schema — ResearchPack: add a round-trip serialization test.
- [x] **T029** Schema — Manuscript: define fields and types.
- [x] **T030** Schema — Manuscript: add field validators.
- [x] **T031** Schema — Manuscript: document an example payload.
- [x] **T032** Schema — Manuscript: add a round-trip serialization test.
- [x] **T033** Schema — ReviewReport: define fields and types.
- [x] **T034** Schema — ReviewReport: add field validators.
- [x] **T035** Schema — ReviewReport: document an example payload.
- [x] **T036** Schema — ReviewReport: add a round-trip serialization test.
- [x] **T037** Schema — LatexSpec: define fields and types.
- [x] **T038** Schema — LatexSpec: add field validators.
- [x] **T039** Schema — LatexSpec: document an example payload.
- [x] **T040** Schema — LatexSpec: add a round-trip serialization test.
- [x] **T041** Schema — ValidationReport: define fields and types.
- [x] **T042** Schema — ValidationReport: add field validators.
- [x] **T043** Schema — ValidationReport: document an example payload.
- [x] **T044** Schema — ValidationReport: add a round-trip serialization test.
- [x] **T045** Schema — CitationReport: define fields and types.
- [x] **T046** Schema — CitationReport: add field validators.
- [x] **T047** Schema — CitationReport: document an example payload.
- [x] **T048** Schema — CitationReport: add a round-trip serialization test.
- [x] **T049** Schema — SourceRegistryEntry: define fields and types.
- [x] **T050** Schema — SourceRegistryEntry: add field validators.
- [x] **T051** Schema — SourceRegistryEntry: document an example payload.
- [x] **T052** Schema — SourceRegistryEntry: add a round-trip serialization test.
- [x] **T053** Schema — AssetSpec: define fields and types.
- [x] **T054** Schema — AssetSpec: add field validators.
- [x] **T055** Schema — AssetSpec: document an example payload.
- [x] **T056** Schema — AssetSpec: add a round-trip serialization test.
- [x] **T057** Schema — EvidenceReport: define fields and types.
- [x] **T058** Schema — EvidenceReport: add field validators.
- [x] **T059** Schema — EvidenceReport: document an example payload.
- [x] **T060** Schema — EvidenceReport: add a round-trip serialization test.

## Phase C — Harness

### D. Citation Manager

- [x] **T061** Load `data/input/source_registry.json` into typed entries
- [x] **T062** Generate valid BibTeX entries from the registry
- [x] **T063** Escape BibTeX special characters safely
- [x] **T064** Generate unique, collision-free citation keys
- [x] **T065** Extract citation markers from Markdown manuscripts
- [x] **T066** Extract citation markers from LaTeX manuscripts
- [x] **T067** Reconcile manuscript markers against known sources
- [x] **T068** Report unresolved citation keys
- [x] **T069** Report unused (uncited) sources
- [x] **T070** Write `references.bib` deterministically (idempotent)
- [x] **T071** Emit `citation_report.json`
- [ ] **T072** Add committed-copy option for grader visibility
- [x] **T073** Unit-test BibTeX generation
- [x] **T074** Unit-test key extraction (Markdown + LaTeX)
- [x] **T075** Unit-test unresolved-key detection

### E. Graph Generator

- [x] **T076** Define the pipeline node sequence
- [x] **T077** Render the agent pipeline graph with matplotlib
- [x] **T078** Style nodes (boxes, colors, arrows) professionally
- [x] **T079** Write PNG to `generated/assets/graphs/`
- [x] **T080** Make output path configurable
- [x] **T081** Ensure deterministic rendering
- [x] **T082** Remove unused locals (ruff clean)
- [x] **T083** Unit-test graph file creation

### F. Document Validator

- [x] **T084** Check required intermediate artifacts exist
- [x] **T085** Validate cover-page metadata present
- [x] **T086** Validate table-of-contents flag
- [x] **T087** Validate chapters and sections present
- [x] **T088** Validate at least one image asset
- [x] **T089** Validate Python-generated graph asset
- [x] **T090** Validate at least one table
- [x] **T091** Validate at least one display formula
- [x] **T092** Validate Hebrew-English BiDi section via Unicode ranges
- [x] **T093** Validate `.bib` exists and keys resolve
- [x] **T094** Validate `latex_spec` references existing files
- [x] **T095** Aggregate results into `validation_report.json`
- [x] **T096** Make validation messages actionable
- [x] **T097** Unit-test each feature check

### G. Asset Generator (future)

- [x] **T098** Create `harness/assets.py` module
- [x] **T099** Generate/collect the required image asset
- [x] **T100** Prepare table data structures
- [x] **T101** Prepare formula metadata
- [x] **T102** Resolve asset file references for the renderer
- [x] **T103** Validate asset references against generated files
- [x] **T104** Unit-test asset preparation

### H. Evidence Reporter (future)

- [x] **T105** Create `harness/evidence.py` module
- [x] **T106** Collect PDF path and build status
- [x] **T107** Collect requirement checklist results
- [x] **T108** Collect token/cost summary if available
- [x] **T109** Collect known limitations
- [x] **T110** Emit `final_report.md`
- [x] **T111** Unit-test evidence aggregation

## Phase D — Orchestration

### I. Agents

- [x] **T112** Agent — Planner: define role.
- [x] **T113** Agent — Planner: define goal.
- [x] **T114** Agent — Planner: craft backstory/system prompt.
- [x] **T115** Agent — Planner: set tools policy.
- [x] **T116** Agent — Planner: provide a dry-run fallback object.
- [x] **T117** Agent — Planner: add a factory unit test.
- [x] **T118** Agent — Planner: tune prompt from reviewer feedback.
- [x] **T119** Agent — Planner: document in PROMPTS.md.
- [x] **T120** Agent — Research: define role.
- [x] **T121** Agent — Research: define goal.
- [x] **T122** Agent — Research: craft backstory/system prompt.
- [x] **T123** Agent — Research: set tools policy.
- [x] **T124** Agent — Research: provide a dry-run fallback object.
- [x] **T125** Agent — Research: add a factory unit test.
- [x] **T126** Agent — Research: tune prompt from reviewer feedback.
- [x] **T127** Agent — Research: document in PROMPTS.md.
- [x] **T128** Agent — Writer: define role.
- [x] **T129** Agent — Writer: define goal.
- [x] **T130** Agent — Writer: craft backstory/system prompt.
- [x] **T131** Agent — Writer: set tools policy.
- [x] **T132** Agent — Writer: provide a dry-run fallback object.
- [x] **T133** Agent — Writer: add a factory unit test.
- [x] **T134** Agent — Writer: tune prompt from reviewer feedback.
- [x] **T135** Agent — Writer: document in PROMPTS.md.
- [x] **T136** Agent — Reviewer: define role.
- [x] **T137** Agent — Reviewer: define goal.
- [x] **T138** Agent — Reviewer: craft backstory/system prompt.
- [x] **T139** Agent — Reviewer: set tools policy.
- [x] **T140** Agent — Reviewer: provide a dry-run fallback object.
- [x] **T141** Agent — Reviewer: add a factory unit test.
- [x] **T142** Agent — Reviewer: tune prompt from reviewer feedback.
- [x] **T143** Agent — Reviewer: document in PROMPTS.md.
- [x] **T144** Agent — LaTeX: define role.
- [x] **T145** Agent — LaTeX: define goal.
- [x] **T146** Agent — LaTeX: craft backstory/system prompt.
- [x] **T147** Agent — LaTeX: set tools policy.
- [x] **T148** Agent — LaTeX: provide a dry-run fallback object.
- [x] **T149** Agent — LaTeX: add a factory unit test.
- [x] **T150** Agent — LaTeX: tune prompt from reviewer feedback.
- [x] **T151** Agent — LaTeX: document in PROMPTS.md.

### J. Tasks

- [x] **T152** Task — Planning: write description.
- [x] **T153** Task — Planning: define expected_output.
- [x] **T154** Task — Planning: wire context dependencies.
- [x] **T155** Task — Planning: map to output artifact.
- [x] **T156** Task — Planning: validate output against its schema.
- [x] **T157** Task — Planning: add a factory unit test.
- [x] **T158** Task — Research: write description.
- [x] **T159** Task — Research: define expected_output.
- [x] **T160** Task — Research: wire context dependencies.
- [x] **T161** Task — Research: map to output artifact.
- [x] **T162** Task — Research: validate output against its schema.
- [x] **T163** Task — Research: add a factory unit test.
- [x] **T164** Task — Writing: write description.
- [x] **T165** Task — Writing: define expected_output.
- [x] **T166** Task — Writing: wire context dependencies.
- [x] **T167** Task — Writing: map to output artifact.
- [x] **T168** Task — Writing: validate output against its schema.
- [x] **T169** Task — Writing: add a factory unit test.
- [x] **T170** Task — Review: write description.
- [x] **T171** Task — Review: define expected_output.
- [x] **T172** Task — Review: wire context dependencies.
- [x] **T173** Task — Review: map to output artifact.
- [x] **T174** Task — Review: validate output against its schema.
- [x] **T175** Task — Review: add a factory unit test.
- [x] **T176** Task — LaTeX-spec: write description.
- [x] **T177** Task — LaTeX-spec: define expected_output.
- [x] **T178** Task — LaTeX-spec: wire context dependencies.
- [x] **T179** Task — LaTeX-spec: map to output artifact.
- [x] **T180** Task — LaTeX-spec: validate output against its schema.
- [x] **T181** Task — LaTeX-spec: add a factory unit test.

### K. Crew & Process

- [x] **T182** Implement `build_crew()` assembling five agents and five tasks
- [x] **T183** Configure `Process.sequential`
- [x] **T184** Provide a `DryRunCrew` fallback when CrewAI is absent
- [x] **T185** Implement `run_crew()` with dry-run as default
- [x] **T186** Guard real execution behind `--run-crew` + `OPENAI_API_KEY`
- [x] **T187** Create-or-reuse dry-run artifacts from sample data
- [x] **T188** Describe the assembled crew (agent/task/process counts)
- [x] **T189** Keep `crew.py` within the 150-line limit (split if needed)
- [x] **T190** Unit-test crew assembly
- [x] **T191** Unit-test dry-run artifact creation
- [x] **T192** Unit-test refusal without an API key

### L. Real Execution (Milestone 5)

- [ ] **T193** Confirm provider, model, and milestone scope with the user
- [ ] **T194** Wire `crew.kickoff()` behind the opt-in flag
- [ ] **T195** Inject the topic from config into task descriptions
- [ ] **T196** Persist real task outputs to `generated/intermediate/`
- [ ] **T197** Keep `sample_*` files as committed examples
- [ ] **T198** Capture token usage from the result
- [ ] **T199** Handle provider/API errors gracefully
- [ ] **T200** Add an opt-in, key-guarded integration test (skipped without key)
- [ ] **T201** Document the real-run command and prerequisites
- [ ] **T202** Update IMPLEMENTATION_STATUS after the run

## Phase E — LaTeX

### M. Templates

- [x] **T203** Template — main.tex.j2: create the Jinja2 file.
- [x] **T204** Template — main.tex.j2: parametrize its fields.
- [x] **T205** Template — main.tex.j2: apply LaTeX escaping to inserted text.
- [x] **T206** Template — main.tex.j2: render-test with sample data.
- [ ] **T207** Template — main.tex.j2: review for page-margin overflow.
- [x] **T208** Template — cover.tex.j2: create the Jinja2 file.
- [x] **T209** Template — cover.tex.j2: parametrize its fields.
- [x] **T210** Template — cover.tex.j2: apply LaTeX escaping to inserted text.
- [x] **T211** Template — cover.tex.j2: render-test with sample data.
- [ ] **T212** Template — cover.tex.j2: review for page-margin overflow.
- [x] **T213** Template — chapter.tex.j2: create the Jinja2 file.
- [x] **T214** Template — chapter.tex.j2: parametrize its fields.
- [x] **T215** Template — chapter.tex.j2: apply LaTeX escaping to inserted text.
- [x] **T216** Template — chapter.tex.j2: render-test with sample data.
- [ ] **T217** Template — chapter.tex.j2: review for page-margin overflow.
- [x] **T218** Template — table.tex.j2: create the Jinja2 file.
- [x] **T219** Template — table.tex.j2: parametrize its fields.
- [x] **T220** Template — table.tex.j2: apply LaTeX escaping to inserted text.
- [x] **T221** Template — table.tex.j2: render-test with sample data.
- [ ] **T222** Template — table.tex.j2: review for page-margin overflow.
- [x] **T223** Template — formula.tex.j2: create the Jinja2 file.
- [x] **T224** Template — formula.tex.j2: parametrize its fields.
- [x] **T225** Template — formula.tex.j2: apply LaTeX escaping to inserted text.
- [x] **T226** Template — formula.tex.j2: render-test with sample data.
- [ ] **T227** Template — formula.tex.j2: review for page-margin overflow.

### N. Renderer

- [x] **T228** Create `latex/renderer.py` (LatexRenderer)
- [x] **T229** Load `latex_spec.json` and the reviewed manuscript
- [x] **T230** Render `main.tex` from the main template
- [ ] **T231** Render per-chapter `.tex` files
- [x] **T232** Insert `\tableofcontents`
- [x] **T233** Insert the cover page with metadata
- [x] **T234** Insert `\includegraphics` for the Python graph
- [x] **T235** Insert `\includegraphics` for the image
- [x] **T236** Render a real LaTeX table
- [x] **T237** Render a display-math formula
- [x] **T238** Render the Hebrew-English BiDi chapter
- [x] **T239** Insert `\printbibliography` / bibliography commands
- [ ] **T240** Copy assets into the build directory
- [x] **T241** Copy `references.bib` into the build directory
- [x] **T242** Keep renderer files within the 150-line limit
- [x] **T243** Add `tests/unit/test_latex_renderer.py`

### O. Escaping

- [x] **T244** Escaping — &: implement the escape rule.
- [x] **T245** Escaping — &: unit-test the escape rule.
- [x] **T246** Escaping — %: implement the escape rule.
- [x] **T247** Escaping — %: unit-test the escape rule.
- [x] **T248** Escaping — $: implement the escape rule.
- [x] **T249** Escaping — $: unit-test the escape rule.
- [x] **T250** Escaping — #: implement the escape rule.
- [x] **T251** Escaping — #: unit-test the escape rule.
- [x] **T252** Escaping — _: implement the escape rule.
- [x] **T253** Escaping — _: unit-test the escape rule.
- [x] **T254** Escaping — {: implement the escape rule.
- [x] **T255** Escaping — {: unit-test the escape rule.
- [x] **T256** Escaping — }: implement the escape rule.
- [x] **T257** Escaping — }: unit-test the escape rule.
- [x] **T258** Escaping — ~: implement the escape rule.
- [x] **T259** Escaping — ~: unit-test the escape rule.
- [x] **T260** Escaping — ^: implement the escape rule.
- [x] **T261** Escaping — ^: unit-test the escape rule.
- [x] **T262** Escaping — \: implement the escape rule.
- [x] **T263** Escaping — \: unit-test the escape rule.

### P. PDF Compiler

- [x] **T264** Create `latex/compiler.py` (PDFCompiler)
- [x] **T265** Detect the LaTeX toolchain on PATH
- [x] **T266** Run pass 1: lualatex
- [x] **T267** Run biber for the bibliography
- [x] **T268** Run pass 2: lualatex
- [x] **T269** Run pass 3: lualatex
- [ ] **T270** Implement the XeLaTeX fallback path
- [x] **T271** Capture and persist `build.log`
- [ ] **T272** Detect unresolved references (`??`) in the log
- [x] **T273** Fail gracefully when no toolchain is present
- [ ] **T274** Emit `final.pdf` to `generated/pdf/`
- [ ] **T275** Verify the PDF is non-empty
- [ ] **T276** Add `tests/integration/test_pdf_build_smoke.py` (skip without toolchain)

## Phase F — Deliverables

### Q. Assignment Requirements

- [ ] **T277** Requirement — Cover page: specify in book_plan.
- [ ] **T278** Requirement — Cover page: place in latex_spec.
- [ ] **T279** Requirement — Cover page: implement renderer support.
- [ ] **T280** Requirement — Cover page: produce/author the artifact.
- [ ] **T281** Requirement — Cover page: validate via DocumentValidator.
- [ ] **T282** Requirement — Cover page: verify in the compiled PDF.
- [ ] **T283** Requirement — Table of contents: specify in book_plan.
- [ ] **T284** Requirement — Table of contents: place in latex_spec.
- [ ] **T285** Requirement — Table of contents: implement renderer support.
- [ ] **T286** Requirement — Table of contents: produce/author the artifact.
- [ ] **T287** Requirement — Table of contents: validate via DocumentValidator.
- [ ] **T288** Requirement — Table of contents: verify in the compiled PDF.
- [ ] **T289** Requirement — Chapters & sections (>=15 pages): specify in book_plan.
- [ ] **T290** Requirement — Chapters & sections (>=15 pages): place in latex_spec.
- [ ] **T291** Requirement — Chapters & sections (>=15 pages): implement renderer support.
- [ ] **T292** Requirement — Chapters & sections (>=15 pages): produce/author the artifact.
- [ ] **T293** Requirement — Chapters & sections (>=15 pages): validate via DocumentValidator.
- [ ] **T294** Requirement — Chapters & sections (>=15 pages): verify in the compiled PDF.
- [ ] **T295** Requirement — Image: specify in book_plan.
- [ ] **T296** Requirement — Image: place in latex_spec.
- [ ] **T297** Requirement — Image: implement renderer support.
- [ ] **T298** Requirement — Image: produce/author the artifact.
- [ ] **T299** Requirement — Image: validate via DocumentValidator.
- [ ] **T300** Requirement — Image: verify in the compiled PDF.
- [ ] **T301** Requirement — Python-generated graph: specify in book_plan.
- [ ] **T302** Requirement — Python-generated graph: place in latex_spec.
- [ ] **T303** Requirement — Python-generated graph: implement renderer support.
- [ ] **T304** Requirement — Python-generated graph: produce/author the artifact.
- [ ] **T305** Requirement — Python-generated graph: validate via DocumentValidator.
- [ ] **T306** Requirement — Python-generated graph: verify in the compiled PDF.
- [ ] **T307** Requirement — Table: specify in book_plan.
- [ ] **T308** Requirement — Table: place in latex_spec.
- [ ] **T309** Requirement — Table: implement renderer support.
- [ ] **T310** Requirement — Table: produce/author the artifact.
- [ ] **T311** Requirement — Table: validate via DocumentValidator.
- [ ] **T312** Requirement — Table: verify in the compiled PDF.
- [ ] **T313** Requirement — Mathematical formula: specify in book_plan.
- [ ] **T314** Requirement — Mathematical formula: place in latex_spec.
- [ ] **T315** Requirement — Mathematical formula: implement renderer support.
- [ ] **T316** Requirement — Mathematical formula: produce/author the artifact.
- [ ] **T317** Requirement — Mathematical formula: validate via DocumentValidator.
- [ ] **T318** Requirement — Mathematical formula: verify in the compiled PDF.
- [ ] **T319** Requirement — Hebrew-English BiDi chapter: specify in book_plan.
- [ ] **T320** Requirement — Hebrew-English BiDi chapter: place in latex_spec.
- [ ] **T321** Requirement — Hebrew-English BiDi chapter: implement renderer support.
- [ ] **T322** Requirement — Hebrew-English BiDi chapter: produce/author the artifact.
- [ ] **T323** Requirement — Hebrew-English BiDi chapter: validate via DocumentValidator.
- [ ] **T324** Requirement — Hebrew-English BiDi chapter: verify in the compiled PDF.
- [ ] **T325** Requirement — Bibliography & citations: specify in book_plan.
- [ ] **T326** Requirement — Bibliography & citations: place in latex_spec.
- [ ] **T327** Requirement — Bibliography & citations: implement renderer support.
- [ ] **T328** Requirement — Bibliography & citations: produce/author the artifact.
- [ ] **T329** Requirement — Bibliography & citations: validate via DocumentValidator.
- [ ] **T330** Requirement — Bibliography & citations: verify in the compiled PDF.
- [ ] **T331** Requirement — Final PDF: specify in book_plan.
- [ ] **T332** Requirement — Final PDF: place in latex_spec.
- [ ] **T333** Requirement — Final PDF: implement renderer support.
- [ ] **T334** Requirement — Final PDF: produce/author the artifact.
- [ ] **T335** Requirement — Final PDF: validate via DocumentValidator.
- [ ] **T336** Requirement — Final PDF: verify in the compiled PDF.

## Phase G — Content

### R. Chapter Authoring

- [ ] **T337** Chapter — From Prompt to Crew: outline the chapter.
- [ ] **T338** Chapter — From Prompt to Crew: draft the prose.
- [ ] **T339** Chapter — From Prompt to Crew: insert citation markers.
- [ ] **T340** Chapter — From Prompt to Crew: reviewer pass for clarity.
- [ ] **T341** Chapter — From Prompt to Crew: render the chapter to .tex.
- [ ] **T342** Chapter — Agent Roles & Tasks: outline the chapter.
- [ ] **T343** Chapter — Agent Roles & Tasks: draft the prose.
- [ ] **T344** Chapter — Agent Roles & Tasks: insert citation markers.
- [ ] **T345** Chapter — Agent Roles & Tasks: reviewer pass for clarity.
- [ ] **T346** Chapter — Agent Roles & Tasks: render the chapter to .tex.
- [ ] **T347** Chapter — Sequential Orchestration: outline the chapter.
- [ ] **T348** Chapter — Sequential Orchestration: draft the prose.
- [ ] **T349** Chapter — Sequential Orchestration: insert citation markers.
- [ ] **T350** Chapter — Sequential Orchestration: reviewer pass for clarity.
- [ ] **T351** Chapter — Sequential Orchestration: render the chapter to .tex.
- [ ] **T352** Chapter — The Deterministic Harness: outline the chapter.
- [ ] **T353** Chapter — The Deterministic Harness: draft the prose.
- [ ] **T354** Chapter — The Deterministic Harness: insert citation markers.
- [ ] **T355** Chapter — The Deterministic Harness: reviewer pass for clarity.
- [ ] **T356** Chapter — The Deterministic Harness: render the chapter to .tex.
- [ ] **T357** Chapter — LaTeX Production & BiDi: outline the chapter.
- [ ] **T358** Chapter — LaTeX Production & BiDi: draft the prose.
- [ ] **T359** Chapter — LaTeX Production & BiDi: insert citation markers.
- [ ] **T360** Chapter — LaTeX Production & BiDi: reviewer pass for clarity.
- [ ] **T361** Chapter — LaTeX Production & BiDi: render the chapter to .tex.
- [ ] **T362** Chapter — Conclusion: outline the chapter.
- [ ] **T363** Chapter — Conclusion: draft the prose.
- [ ] **T364** Chapter — Conclusion: insert citation markers.
- [ ] **T365** Chapter — Conclusion: reviewer pass for clarity.
- [ ] **T366** Chapter — Conclusion: render the chapter to .tex.

### S. BiDi Hebrew-English

- [ ] **T367** Choose a BiDi chapter topic
- [ ] **T368** Draft the Hebrew passage
- [ ] **T369** Interleave English technical terms
- [ ] **T370** Verify correct LTR/RTL transitions in source
- [ ] **T371** Select polyglossia/bidi packages
- [ ] **T372** Render the BiDi chapter to .tex
- [ ] **T373** Verify BiDi correctness in the compiled PDF

## Phase H — Testing

### T. Unit & Integration Tests

- [ ] **T374** Tests — config: write happy-path unit tests.
- [ ] **T375** Tests — config: write edge-case/error tests.
- [ ] **T376** Tests — config: check coverage contribution.
- [ ] **T377** Tests — schemas: write happy-path unit tests.
- [ ] **T378** Tests — schemas: write edge-case/error tests.
- [ ] **T379** Tests — schemas: check coverage contribution.
- [ ] **T380** Tests — validators: write happy-path unit tests.
- [ ] **T381** Tests — validators: write edge-case/error tests.
- [ ] **T382** Tests — validators: check coverage contribution.
- [ ] **T383** Tests — citations: write happy-path unit tests.
- [ ] **T384** Tests — citations: write edge-case/error tests.
- [ ] **T385** Tests — citations: check coverage contribution.
- [ ] **T386** Tests — graph_generator: write happy-path unit tests.
- [ ] **T387** Tests — graph_generator: write edge-case/error tests.
- [ ] **T388** Tests — graph_generator: check coverage contribution.
- [ ] **T389** Tests — orchestration_agents: write happy-path unit tests.
- [ ] **T390** Tests — orchestration_agents: write edge-case/error tests.
- [ ] **T391** Tests — orchestration_agents: check coverage contribution.
- [ ] **T392** Tests — orchestration_tasks: write happy-path unit tests.
- [ ] **T393** Tests — orchestration_tasks: write edge-case/error tests.
- [ ] **T394** Tests — orchestration_tasks: check coverage contribution.
- [ ] **T395** Tests — orchestration_crew: write happy-path unit tests.
- [ ] **T396** Tests — orchestration_crew: write edge-case/error tests.
- [ ] **T397** Tests — orchestration_crew: check coverage contribution.
- [ ] **T398** Tests — latex_renderer: write happy-path unit tests.
- [ ] **T399** Tests — latex_renderer: write edge-case/error tests.
- [ ] **T400** Tests — latex_renderer: check coverage contribution.
- [ ] **T401** Tests — latex_compiler: write happy-path unit tests.
- [ ] **T402** Tests — latex_compiler: write edge-case/error tests.
- [ ] **T403** Tests — latex_compiler: check coverage contribution.
- [ ] **T404** Tests — assets: write happy-path unit tests.
- [ ] **T405** Tests — assets: write edge-case/error tests.
- [ ] **T406** Tests — assets: check coverage contribution.
- [ ] **T407** Tests — evidence: write happy-path unit tests.
- [ ] **T408** Tests — evidence: write edge-case/error tests.
- [ ] **T409** Tests — evidence: check coverage contribution.
- [ ] **T410** Tests — version: write happy-path unit tests.
- [ ] **T411** Tests — version: write edge-case/error tests.
- [ ] **T412** Tests — version: check coverage contribution.
- [ ] **T413** Tests — main: write happy-path unit tests.
- [ ] **T414** Tests — main: write edge-case/error tests.
- [ ] **T415** Tests — main: check coverage contribution.

### U. Coverage & Lint Gates

- [ ] **T416** Add `[tool.ruff]` configuration
- [ ] **T417** Add `[tool.coverage]` with `fail_under = 85`
- [ ] **T418** Add ruff/pytest-cov to the dev dependency group
- [ ] **T419** Run `ruff check` to zero violations
- [ ] **T420** Run `pytest --cov` and record the percentage
- [ ] **T421** Raise coverage to >= 85% by adding tests
- [x] **T422** Add a `conftest.py` for shared fixtures
- [ ] **T423** Mock external dependencies in tests
- [ ] **T424** Ensure no test depends on a network/API
- [ ] **T425** Document the test and lint commands

## Phase I — Compliance

### V. Mandatory Documentation

- [x] **T426** Create `docs/PRD.md`
- [x] **T427** Create `docs/PLAN.md`
- [x] **T428** Create `docs/TODO.md` (this file)
- [x] **T429** Create `docs/PROMPTS.md` (prompt log)
- [x] **T430** Create per-mechanism `docs/PRD_latex_pipeline.md`
- [x] **T431** Create per-mechanism `docs/PRD_citation_management.md`
- [x] **T432** Keep README concise and link to docs
- [x] **T433** Maintain `docs/COURSE_ALIGNMENT.md`
- [x] **T434** Maintain `docs/ARCHITECTURE_DIAGRAM.md`
- [x] **T435** Maintain `docs/IMPLEMENTATION_STATUS.md`

### W. Engineering Standards

- [ ] **T436** Enforce the 150-line-per-file limit across `src/`
- [ ] **T437** Split `crew.py` into focused modules
- [ ] **T438** Introduce an SDK single entry point (`sdk/`)
- [ ] **T439** Route all business logic through the SDK
- [ ] **T440** Remove any code duplication (DRY)
- [ ] **T441** Add docstrings to every public function/module
- [ ] **T442** Ensure comments explain 'why', not 'what'
- [ ] **T443** Generate and commit `uv.lock`
- [ ] **T444** Verify no `pip`/`python -m` calls anywhere
- [ ] **T445** Verify ISO/IEC 25010 quality characteristics are addressed

### X. Security & Secrets

- [ ] **T446** Confirm no API keys/secrets in source
- [ ] **T447** Confirm `.env` is git-ignored
- [ ] **T448** Confirm `.env-example` holds only dummy values
- [ ] **T449** Confirm `.gitignore` covers `*.key`, `*.pem`, `credentials.json`
- [ ] **T450** Access secrets only via environment variables
- [ ] **T451** Document least-privilege/key-rotation guidance
- [ ] **T452** Scan tracked files for accidental secret patterns

## Phase J — Ops

### Y. Observability & Cost

- [ ] **T453** Log each task's inputs and outputs
- [ ] **T454** Persist intermediate artifacts for inspection
- [ ] **T455** Record execution mode (dry-run vs real)
- [ ] **T456** Capture token usage per run
- [ ] **T457** Build a cost table by model
- [ ] **T458** Estimate total cost per full run
- [ ] **T459** Add budget overrun alerts (config-driven)
- [ ] **T460** Produce a per-run observability summary

### Z. Packaging & Distribution

- [ ] **T461** Confirm `pyproject.toml` package metadata
- [ ] **T462** Ensure `__init__.py` exports public interfaces
- [ ] **T463** Expose the `bookgen` console script entry point
- [ ] **T464** Use relative/package paths (no absolute paths)
- [ ] **T465** Verify the package builds cleanly
- [ ] **T466** Document installation from a clean clone

### AA. Git & Version Control

- [ ] **T467** Use feature branches per milestone
- [ ] **T468** Write meaningful commit messages
- [ ] **T469** Open pull requests with review
- [ ] **T470** Tag major versions
- [ ] **T471** Maintain a prompt-engineering log alongside commits
- [ ] **T472** Reconcile author metadata with the submitting student
- [ ] **T473** Keep `generated/` out of version control

## Phase K — Submission

### AB. Documentation Reconciliation

- [ ] **T474** Reconcile milestone numbering (Blueprint vs Status)
- [ ] **T475** Fix stale absolute `cd` paths in docs
- [ ] **T476** Standardize the citation report filename
- [ ] **T477** Pick a canonical manuscript format (md vs json)
- [ ] **T478** Align the PDF engine references across docs
- [ ] **T479** Mark generated-vs-committed files clearly

### AC. Final Submission Checklist

- [ ] **T480** All mandatory docs present (PRD/PLAN/TODO)
- [ ] **T481** Per-mechanism PRDs present
- [ ] **T482** Ruff = 0 violations
- [ ] **T483** Coverage >= 85%
- [ ] **T484** All files <= 150 lines
- [ ] **T485** `uv.lock` committed
- [ ] **T486** `.env-example` present, no secrets
- [ ] **T487** Cover page shows correct author/course/lecturer/date
- [ ] **T488** Table of contents renders
- [ ] **T489** Document is >= 15 pages
- [ ] **T490** Image present and rendered
- [ ] **T491** Python graph embedded
- [ ] **T492** Table rendered
- [ ] **T493** Formula typeset (not plain text)
- [ ] **T494** BiDi chapter renders correctly
- [ ] **T495** Bibliography resolves with working citations
- [ ] **T496** Final PDF compiles end-to-end
- [ ] **T497** Build log captured
- [ ] **T498** Validation report green
- [ ] **T499** README evidence and screenshots added
- [ ] **T500** Repository cleaned for submission
- [ ] **T501** Tag the submission version
- [ ] **T502** Final grader walkthrough prepared

## Phase L — Research & Analysis

### AD. Parameter Research (guideline 9)

- [ ] **T503** Identify parameters to study (chunk size, overlap, temperature, model)
- [ ] **T504** Design One-At-a-Time (OAT) sensitivity experiments
- [ ] **T505** Run controlled experiments and record results
- [ ] **T506** Build a results-analysis Jupyter notebook
- [ ] **T507** Compare models/configurations quantitatively
- [ ] **T508** Write equations in LaTeX inside the notebook
- [ ] **T509** Add academic references to the analysis
- [ ] **T510** Export a bar chart for comparisons
- [ ] **T511** Export a line chart for trends
- [ ] **T512** Export a scatter plot for correlations
- [ ] **T513** Export a heatmap for parameter sensitivity
- [ ] **T514** Export a box plot for distributions
- [ ] **T515** Ensure high-resolution figures with clear captions
- [ ] **T516** Summarize findings and recommendations

### AE. Edge Cases & Error Handling (guideline 6.3)

- [ ] **T517** Enumerate boundary conditions per component
- [ ] **T518** Handle missing/invalid config gracefully
- [ ] **T519** Handle missing intermediate artifacts
- [ ] **T520** Handle empty/oversized manuscripts
- [ ] **T521** Handle unresolved citations before compile
- [ ] **T522** Handle missing LaTeX toolchain
- [ ] **T523** Add defensive input validation with clear messages
- [ ] **T524** Log failures with actionable detail

### AF. UI/UX & Interface Docs (guideline 10)

- [ ] **T525** Document each CLI workflow end-to-end
- [ ] **T526** Write clear `--help` text for every flag
- [ ] **T527** Make error messages user-friendly
- [ ] **T528** Capture screenshots of representative runs
- [ ] **T529** Apply Nielsen usability heuristics to the CLI
- [ ] **T530** Document accessibility considerations
- [ ] **T531** Describe typical user journeys

### AG. Costs & Pricing (guideline 11)

- [ ] **T532** Count input/output tokens per run
- [ ] **T533** Compute cost per million tokens by model
- [ ] **T534** Build a token-cost table
- [ ] **T535** Forecast total cost for a full generation
- [ ] **T536** Document token-reduction/optimization strategies
- [ ] **T537** Add budget alerts driven by `config/budgets.json`

### AH. Maintainability & Extension (guideline 12)

- [ ] **T538** Document plugin/extension points
- [ ] **T539** Define lifecycle hooks for the pipeline
- [ ] **T540** Describe a middleware mechanism for stages
- [ ] **T541** Publish clear extension interfaces
- [ ] **T542** Review separation of concerns
- [ ] **T543** Review debuggability and reuse

### AI. Parallelism & Performance (guideline 15)

- [ ] **T544** Identify I/O-bound vs CPU-bound steps
- [ ] **T545** Choose threads vs processes appropriately
- [ ] **T546** Use `queue.Queue` for safe data transfer
- [ ] **T547** Protect shared state with locks
- [ ] **T548** Avoid deadlocks and race conditions
- [ ] **T549** Benchmark stage latencies
- [ ] **T550** Produce a performance spec sheet (latency/memory/tokens)

### AJ. Modular Building Blocks (guideline 16)

- [ ] **T551** Define inputs/outputs/setup for each block
- [ ] **T552** Enforce single responsibility per block
- [ ] **T553** Use dependency injection for testability
- [ ] **T554** Review block reusability and independence
- [ ] **T555** Apply the Template Method for varied-but-similar logic
- [ ] **T556** Enforce mixin rules (single concern, independently testable)
- [ ] **T557** Document each block's contract

### AK. ISO/IEC 25010 Quality (guideline 13)

- [ ] **T558** Address functional suitability
- [ ] **T559** Address performance efficiency
- [ ] **T560** Address compatibility
- [ ] **T561** Address usability
- [ ] **T562** Address reliability
- [ ] **T563** Address security
- [ ] **T564** Address maintainability
- [ ] **T565** Address portability

## Phase M — Audit Gap Closure (untracked items found in re-audit)

> These items were surfaced by the materials-vs-repo re-audit and were not
> previously tracked above. They are doc/code gaps; only the relevant doc edits
> have been applied so far.

### AL. API Gatekeeper & Rate Limiting (guideline 5)

- [ ] **T566** Create `src/bookgen/shared/gatekeeper.py` as the single monitored entry to the LLM provider
- [ ] **T567** Route all CrewAI/provider calls through the gatekeeper (no direct calls)
- [ ] **T568** Add retry, logging, and monitoring inside the gatekeeper
- [ ] **T569** Create versioned `config/rate_limits.json` (requests_per_minute, requests_per_hour, concurrent_max, max_retries, retry_after_seconds)
- [ ] **T570** Enforce rate limits before each provider call
- [ ] **T571** Add a FIFO overflow queue with max depth, backpressure alert, and drain
- [ ] **T572** Unit-test the gatekeeper (rate limit, queue, retry)

### AM. Licensing & Packaging Metadata (guideline 14.1)

- [ ] **T573** Add a `LICENSE` file (choose an appropriate license)
- [ ] **T574** Add the `license` field to `pyproject.toml` `[project]`
- [ ] **T575** Add third-party attribution/credits

### AN. Configuration Completeness (guideline 7.3, 8.1)

- [ ] **T576** Add `config/logging_config.json` and wire `shared/logging.py` to read it
- [x] **T577** Add a `version` key to `budgets.json`, `models.json`, and `latex.json` (done; required field validated by Pydantic)
- [ ] **T578** Implement runtime configuration-version validation (fail on mismatch)
- [ ] **T579** Extract immutable constants into `shared/constants.py` (REQUIRED_AGENTS, EXPECTED_ARTIFACTS, ...)

### AO. Validation Integrity (fix false-green)

- [ ] **T580** Strengthen `validators.py` to assert real artifact files exist on disk (not just spec keys/strings)
- [ ] **T581** Add post-compile checks that features are actually embedded in the PDF
- [ ] **T582** Add `latex/escaping.py` and route all agent-sourced text through it before rendering

### AP. Test Rigor (guideline 6)

- [x] **T583** Enforce the 85% coverage gate via CI (`--cov --cov-fail-under=85`); kept out of pytest addopts so the plain test command still runs
- [x] **T584** Add a test for `shared/logging.py` (now 100% covered)
- [x] **T585** Cover the untested `validators.py` branches (now 100%)

### AQ. Packaging Hygiene (guideline 14.2)

- [x] **T586** Add `__init__.py` to `document/`, `harness/`, `latex/`, `orchestration/` (src subpackages; tests dirs optional)
- [ ] **T587** Export public interfaces / `__all__` from sub-package inits

### AR. Documentation Hygiene & Drift

- [x] **T588** Resolve dual env-example: kept `.env-example` (guideline name), removed `.env.example`, updated doc references
- [ ] **T589** Add README guideline-2.1 sections: Installation, Configuration Guide (per `config/*.json` param), License & Credits
- [ ] **T590** Reconcile/prune FOLDER_STRUCTURE drift: `process.py`, `document/artifacts.py`, `scripts/`, `data/input/project_config.json`, `docs/ADRS.md`
- [ ] **T591** Consolidate legacy root docs (AGENTS_DESIGN/ARCHITECTURE/PROJECT_PLAN/TASK_FLOW/FOLDER_STRUCTURE) into `docs/` or mark superseded
- [ ] **T592** Mark the SDK single-entry-point as planned where PRD/PLAN reference it

### AS. Agent Security (lesson Section 8)

- [ ] **T593** Review prompt-injection, tool-misuse, identity-abuse, and memory-poisoning risks
- [ ] **T594** Run a red-team pass against the agents before any real execution
- [ ] **T595** Document agent-security mitigations and the human-in-the-loop control point

### AT. Automated Quality Tooling (lecturer feedback)

- [x] **T596** Add a formatter (`ruff format`) and document the format command
- [x] **T597** Add a pre-commit hook (lint + format check) shared via `core.hooksPath` (`scripts/hooks/pre-commit`)
- [x] **T598** Add a CI workflow (`.github/workflows/ci.yml`) running ruff + format check + `pytest --cov` on each PR

### AU. Skills (CrewAI course feature + build tooling)

- [x] **T599** Create CrewAI Skill packs under `skills/` (latex-style, citation-discipline, course-alignment)
- [x] **T600** Add `orchestration/skills.py` for skill discovery and per-agent assignment
- [x] **T601** Wire skills into agents via `skills=` (real-crew mode only; dry-run unaffected)
- [x] **T602** Unit-test skill discovery and assignment
- [x] **T603** Add a Claude Code build skill (`.claude/skills/build-bookgen/SKILL.md`)

---

**Total tasks: 603** (278 completed, 325 remaining).

