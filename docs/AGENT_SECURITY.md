# Agent Security Review

This document records the agent-security review for the BookGen CrewAI pipeline,
the red-team pass performed before any real (API-backed) execution, and the
human-in-the-loop control point. It maps directly to lecture L06 §8 (Agent
Security), §9 (Design Principles for Production Systems) and §10 (The Harness):
*"Do not release agents without running a Red Team to attack them."*

## 1. Scope and trust model

An agent is not just a model that returns text — it receives goals, operates
tools, touches identities, and leaves traces in memory. Our risk therefore comes
from the agents' ability to *plan and act*, not merely to generate prose.

What reduces our exposure by design:

- **Dry-run is the default.** `python -m bookgen.main` never calls the model
  provider; it reuses committed sample artifacts. The API path is opt-in only
  (`--run-crew`, and only with `OPENAI_API_KEY` set). No autonomous loop ships
  enabled.
- **No destructive tools are wired in.** The agents author text and a build
  spec; they do not delete files, send mail, or hold standing cloud credentials.
- **Deterministic harness around the model.** Citations, asset generation,
  validation and LaTeX rendering are plain Python (the harness), not model
  decisions — so the model cannot directly control the file system or the build.

## 2. Attack surfaces and mitigations

The four primary attack types from §8, assessed for *this* system:

| # | Attack surface | Risk in BookGen | Mitigation |
|---|---|---|---|
| 1 | **Prompt injection** | A malicious instruction hidden in a topic, a source document, or research text ("ignore instructions and …") could steer the Writer/LaTeX agents. | Agents work *from structured Context only* (no open web tool on the Writer/Reviewer/LaTeX agents). All agent-sourced text is treated as untrusted and **escaped via `latex/escaping.py`** before it reaches a template, so injected `\input`, `\write18`, or backslash payloads become literal characters, not LaTeX commands. Schemas (`document/schemas.py`) constrain shapes so a payload cannot smuggle extra fields. |
| 2 | **Tool misuse** | A legitimate capability used for an unintended effect (e.g. a search/file tool exfiltrating or overwriting data). | The shipped agents have **no file-write or shell tools**; the only external capability (provider call) is routed through `shared/gatekeeper.py` (rate-limit + retry + backpressure), which bounds call volume. LaTeX compilation runs `lualatex`/`biber` as fixed, non-shell-escape commands; we do **not** enable `-shell-escape`. |
| 3 | **Identity abuse** | Uncontrolled use of an API key or the agent's identity. | Secrets are read **only from environment variables** (`.env`, git-ignored); `.env-example` carries dummy values; `.gitignore` covers `*.key`, `*.pem`, `credentials.json`. No key is hard-coded or logged. Least-privilege and key-rotation guidance is in §5 below. |
| 4 | **Memory poisoning** | A "dormant" instruction embedded in persisted state that triggers on a later run. | The pipeline is **stateless across runs** in dry-run: each run regenerates artifacts from versioned config + committed samples; there is no long-lived agent memory store that an earlier run can poison. Intermediate artifacts are written to `generated/` (git-ignored) and are inspectable before reuse. |

## 3. Red-team pass (pre-real-run checklist)

Run these adversarial checks before enabling `--run-crew` against a live provider.
Each is a *defensive* test of our own pipeline:

1. **Injection in the topic** — set the config topic to a string containing
   `\\input{/etc/passwd}` and `Ignore previous instructions`; confirm the rendered
   `main.tex` contains the text *escaped and inert*, and that no file outside the
   project is read.
2. **Injection in a source entry** — add a `source_registry.json` entry whose
   title contains LaTeX control sequences; confirm `references.bib` and citations
   render literally.
3. **Oversized / empty manuscript** — feed an empty and a 10k-section plan;
   confirm validators reject it with a clear message rather than crashing or
   producing a degenerate PDF (see TODO §A boundary tasks).
4. **Tool-surface review** — grep the agent definitions for any tool granting
   file-write, shell, or network write access; confirm there are none on the
   Writer/Reviewer/LaTeX agents.
5. **Secret-leak scan** — scan tracked files for key patterns; confirm no secret
   is committed and that logs never print the API key.
6. **Compile sandboxing** — confirm the LaTeX invocation does not pass
   `-shell-escape`, so a `\write18` in agent text cannot execute a command.

Record the outcome of each check in the run log before promoting to a real run.

## 4. Human-in-the-loop control point

Per §11.4 (Positive vs Negative AI Economy), there must always be a control
point. In BookGen the human gate is explicit and unavoidable:

- The default path is **dry-run**; producing a real, API-backed document is a
  deliberate human action (`--run-crew` with a key the human supplies).
- The **Reviewer agent + the human author** inspect the manuscript before the
  LaTeX spec is built, and the human reviews the compiled PDF before submission.
- No stage auto-publishes or sends the output anywhere external.

If the pipeline is later extended with a Writer↔Reviewer revision loop, the
human-approval gate before compilation must remain mandatory.

## 5. Design-level protections (maps §9) and residual risk

- **Modularity / model-swap via config**, not hard-coding (`config/models.json`).
- **Version management**: every config file carries a `version`; `load_config`
  fails on a version mismatch.
- **Observability**: per-task inputs/outputs and execution mode (dry-run vs real)
  are logged; token usage is captured on real runs (`docs/COSTS.md`).
- **Least privilege / key rotation**: scope the provider key to the minimum
  needed, store it only in the environment, and rotate it on any suspected
  exposure; never reuse a personal key for shared CI.

**Residual risk:** once real tools (web search, file access) are attached to an
agent, surfaces (1) and (2) grow materially. Re-run this red-team pass, add
per-tool allow-lists, and keep the human-in-the-loop gate before any action that
writes outside `generated/` or contacts an external service.
