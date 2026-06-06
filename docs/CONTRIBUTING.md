# Contributing

This project is being built milestone by milestone. Keep changes narrow and update documentation as the project evolves.

## Ground Rules

- Do not implement future milestones early.
- Do not add extra agents without explicit approval.
- Real LLM execution is opt-in via `--run-crew` (requires `OPENAI_API_KEY`); keep dry-run the default.
- PDF compilation is opt-in via `--build-pdf` (requires a TeX toolchain); do not compile PDFs in default/CI runs.
- Keep deterministic components deterministic and testable.
- Update `docs/IMPLEMENTATION_STATUS.md` after each milestone.

## Approved Agent Set

Only these agents are approved for version 1:

- Planner Agent
- Research Agent
- Writer Agent
- Reviewer Agent
- LaTeX Agent

Do not add Citation Agent, Visuals Agent, QA Agent, or Manager Agent in v1.

## Development Workflow

1. Read `docs/PROJECT_BLUEPRINT.md`.
2. Read `docs/IMPLEMENTATION_STATUS.md`.
3. Implement only the requested milestone.
4. Add or update focused tests.
5. Run tests.
6. Update status docs.
7. Summarize changed files and test results.

## Code Standards & Style

All changes must meet these standards before they are merged:

- **Ruff lint, zero violations.** Lint with the configured rule set
  `select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]`; `ruff check .`
  must report **0 violations**.
- **Ruff format.** Run `ruff format .`; the formatter must report no changes.
- **≤ 150 lines per file.** Keep every source file at or under 150 lines; split
  modules (e.g. crew assembly vs. dry-run helpers) instead of growing one file.
- **Docstrings everywhere.** Every module, class, and public function carries a
  docstring describing intent and contract.
- **Descriptive names.** Prefer explicit, intention-revealing names over
  abbreviations.
- **DRY.** Extract shared logic into a single helper rather than duplicating it;
  one block, one responsibility.
- **Tests + 85% coverage gate.** Add or update focused tests for every change;
  `pytest --cov=bookgen` must stay at or above the 85% coverage gate
  (`fail_under = 85` in `pyproject.toml`).

## Testing Command

```powershell
$env:PYTHONPATH="src"
uv run --no-project --with pydantic --with pytest --with pytest-cov --with matplotlib --with jinja2 python -m pytest tests --cov=bookgen
```

Run the full suite (`uv run pytest`). The project currently has **134 passing
tests, 2 skipped** integration tests, and **~94% coverage** (gate 85%). The
coverage gate is enforced via `--cov=bookgen --cov-fail-under=85` (also
configured via `fail_under=85` in `pyproject.toml`).

## Documentation Rules

Keep README concise. Put detailed explanations in `docs/`.

Use:

- `PROJECT_BLUEPRINT.md` for the overall source of truth,
- `COURSE_ALIGNMENT.md` for course concept mapping,
- `ARCHITECTURE_DIAGRAM.md` for diagrams,
- `IMPLEMENTATION_STATUS.md` for milestone status,
- `QUICK_START.md` for commands.

## Future AI Assistant Instructions

If another AI assistant continues the project:

1. Start from `docs/PROJECT_BLUEPRINT.md`.
2. Confirm the current milestone with the user.
3. Avoid API calls unless explicitly requested.
4. Avoid PDF compilation unless explicitly requested.
5. Keep dry-run as the default execution path.
6. Keep responses grounded in the course architecture: Agent, Task, Crew, Process, Context, Harness, Validation, Observability, LaTeX production.
