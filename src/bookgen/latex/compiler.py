"""Deterministic LaTeX -> PDF compilation with graceful degradation.

Runs the configured engine and bibliography backend over multiple passes
(lualatex -> biber -> lualatex -> lualatex) so citations and cross-references
resolve. When the toolchain is absent, it degrades gracefully instead of raising.
A secondary engine (e.g. xelatex) is tried if the primary engine yields no PDF.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

REPRODUCIBLE_TEX_ENV = {"SOURCE_DATE_EPOCH": "1767225600", "FORCE_SOURCE_DATE": "1"}


@dataclass
class CompileResult:
    """Outcome of a LaTeX compilation attempt."""

    success: bool
    pdf_path: Path | None
    log_path: Path | None
    message: str
    commands: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    pages: int | None = None


def toolchain_available(engine: str = "lualatex", bib_backend: str = "biber") -> bool:
    """Return whether the LaTeX engine and bibliography backend are on PATH."""
    return shutil.which(engine) is not None and shutil.which(bib_backend) is not None


def scan_log_issues(log_text: str) -> list[str]:
    """Return human-readable warnings detected in a LaTeX build log."""
    issues: list[str] = []
    if "There were undefined references" in log_text or re.search(
        r"Reference [`'][^']+' on page \d+ undefined", log_text
    ):
        issues.append("unresolved references (??) — a compiler pass is missing")
    if "There were undefined citations" in log_text or re.search(
        r"Citation [`'][^']+'[^\n]*undefined", log_text
    ):
        issues.append("undefined citations — rerun biber / add a pass")
    if "Overfull \\hbox" in log_text:
        issues.append("overfull horizontal box — content may exceed the page margin")
    return issues


def pdf_page_count(log_text: str) -> int | None:
    """Extract the page count reported by the engine, if present."""
    match = re.search(r"Output written on \S+\.pdf \((\d+) page", log_text)
    return int(match.group(1)) if match else None


def _command_sequence(engine: str, bib_backend: str, stem: str, passes: int) -> list[list[str]]:
    sequence = [[engine, "-interaction=nonstopmode", f"{stem}.tex"], [bib_backend, stem]]
    for _ in range(max(passes - 2, 1)):
        sequence.append([engine, "-interaction=nonstopmode", f"{stem}.tex"])
    return sequence


def _run_sequence(commands: list[list[str]], work_dir: Path) -> str:
    chunks: list[str] = []
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=work_dir,
            env=_reproducible_env(),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        chunks.append(f"$ {' '.join(command)}\n{completed.stdout}\n{completed.stderr}")
    return "\n".join(chunks)


def _reproducible_env() -> dict[str, str]:
    env = os.environ.copy()
    for key, value in REPRODUCIBLE_TEX_ENV.items():
        env.setdefault(key, value)
    return env


def compile_pdf(
    tex_path: Path | str,
    engine: str = "lualatex",
    bib_backend: str = "biber",
    passes: int = 4,
    output_dir: Path | str | None = None,
    fallback_engine: str | None = None,
) -> CompileResult:
    """Compile a ``.tex`` file to PDF, capturing a build log and warnings."""
    tex = Path(tex_path)
    work_dir = Path(output_dir) if output_dir else tex.parent
    work_dir.mkdir(parents=True, exist_ok=True)
    log_path = work_dir / "build.log"
    pdf_path = work_dir / f"{tex.stem}.pdf"

    if not toolchain_available(engine, bib_backend):
        message = f"LaTeX toolchain not found ({engine}/{bib_backend}); skipping compilation."
        log_path.write_text(message + "\n", encoding="utf-8")
        return CompileResult(False, None, log_path, message)

    commands = _command_sequence(engine, bib_backend, tex.stem, passes)
    log_text = _run_sequence(commands, work_dir)

    if not pdf_path.exists() and fallback_engine and shutil.which(fallback_engine):
        fallback = _command_sequence(fallback_engine, bib_backend, tex.stem, passes)
        log_text += f"\n[fallback engine: {fallback_engine}]\n" + _run_sequence(fallback, work_dir)
        commands = [*commands, *fallback]

    log_path.write_text(log_text, encoding="utf-8")
    success = pdf_path.exists()

    # Scan the engine's own .log (the final pass only) rather than the concatenated
    # multi-pass build.log, so early-pass "undefined citation/reference" notices
    # that biber and later passes resolve are not reported as real issues.
    engine_log = work_dir / f"{tex.stem}.log"
    final_log = (
        engine_log.read_text(encoding="utf-8", errors="replace")
        if engine_log.exists()
        else log_text
    )
    message = "PDF compiled." if success else "Compilation finished without a PDF; see build.log."
    return CompileResult(
        success=success,
        pdf_path=pdf_path if success else None,
        log_path=log_path,
        message=message,
        commands=[" ".join(command) for command in commands],
        warnings=scan_log_issues(final_log) if success else [],
        pages=pdf_page_count(final_log),
    )
