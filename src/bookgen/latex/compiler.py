"""Deterministic LaTeX -> PDF compilation with graceful degradation.

Runs the configured engine and bibliography backend over multiple passes
(lualatex -> biber -> lualatex -> lualatex) so citations and cross-references
resolve. When the toolchain is absent, it degrades gracefully instead of raising.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CompileResult:
    """Outcome of a LaTeX compilation attempt."""

    success: bool
    pdf_path: Path | None
    log_path: Path | None
    message: str
    commands: list[str] = field(default_factory=list)


def toolchain_available(engine: str = "lualatex", bib_backend: str = "biber") -> bool:
    """Return whether the LaTeX engine and bibliography backend are on PATH."""
    return shutil.which(engine) is not None and shutil.which(bib_backend) is not None


def _command_sequence(engine: str, bib_backend: str, stem: str, passes: int) -> list[list[str]]:
    sequence = [[engine, "-interaction=nonstopmode", f"{stem}.tex"], [bib_backend, stem]]
    for _ in range(max(passes - 2, 1)):
        sequence.append([engine, "-interaction=nonstopmode", f"{stem}.tex"])
    return sequence


def compile_pdf(
    tex_path: Path | str,
    engine: str = "lualatex",
    bib_backend: str = "biber",
    passes: int = 4,
    output_dir: Path | str | None = None,
) -> CompileResult:
    """Compile a ``.tex`` file to PDF, capturing a build log."""
    tex = Path(tex_path)
    work_dir = Path(output_dir) if output_dir else tex.parent
    work_dir.mkdir(parents=True, exist_ok=True)
    log_path = work_dir / "build.log"

    if not toolchain_available(engine, bib_backend):
        message = f"LaTeX toolchain not found ({engine}/{bib_backend}); skipping compilation."
        log_path.write_text(message + "\n", encoding="utf-8")
        return CompileResult(False, None, log_path, message)

    commands = _command_sequence(engine, bib_backend, tex.stem, passes)
    log_chunks: list[str] = []
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=work_dir,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        log_chunks.append(f"$ {' '.join(command)}\n{completed.stdout}\n{completed.stderr}")

    log_path.write_text("\n".join(log_chunks), encoding="utf-8")
    pdf_path = work_dir / f"{tex.stem}.pdf"
    success = pdf_path.exists()
    message = "PDF compiled." if success else "Compilation finished without a PDF; see build.log."
    return CompileResult(
        success=success,
        pdf_path=pdf_path if success else None,
        log_path=log_path,
        message=message,
        commands=[" ".join(command) for command in commands],
    )
