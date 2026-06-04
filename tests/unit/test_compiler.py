"""Tests for the LaTeX PDF compiler (graceful no-toolchain path)."""

from __future__ import annotations

from pathlib import Path

from bookgen.latex.compiler import compile_pdf, toolchain_available


def test_toolchain_available_false_for_missing() -> None:
    assert toolchain_available("no-such-engine-xyz", "no-such-biber") is False


def test_compile_pdf_without_toolchain_is_graceful(tmp_path: Path) -> None:
    tex = tmp_path / "doc.tex"
    tex.write_text(
        "\\documentclass{article}\\begin{document}hi\\end{document}",
        encoding="utf-8",
    )

    result = compile_pdf(tex, engine="no-such-engine-xyz", bib_backend="no-such-biber")

    assert result.success is False
    assert result.pdf_path is None
    assert result.log_path is not None and result.log_path.exists()
    assert "not found" in result.message.lower()
