"""Tests for the LaTeX PDF compiler (graceful no-toolchain path)."""

from __future__ import annotations

from pathlib import Path

from bookgen.latex.compiler import (
    REPRODUCIBLE_TEX_ENV,
    STALE_LATEX_EXTENSIONS,
    _clean_latex_state,
    _reproducible_env,
    compile_pdf,
    pdf_page_count,
    scan_log_issues,
    toolchain_available,
)


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


def test_scan_log_issues_detects_undefined_refs_and_citations() -> None:
    log = "There were undefined references.\nThere were undefined citations.\n"
    issues = scan_log_issues(log)
    assert any("unresolved references" in issue for issue in issues)
    assert any("undefined citations" in issue for issue in issues)


def test_scan_log_issues_detects_overfull_box() -> None:
    issues = scan_log_issues("Overfull \\hbox (12.0pt too wide) in paragraph")
    assert any("overfull" in issue.lower() for issue in issues)


def test_scan_log_issues_clean_log_has_no_issues() -> None:
    assert scan_log_issues("Output written on main.pdf (18 pages).") == []


def test_pdf_page_count_parses_output_line() -> None:
    assert pdf_page_count("Output written on main.pdf (18 pages, 212889 bytes).") == 18


def test_pdf_page_count_returns_none_when_absent() -> None:
    assert pdf_page_count("no page line here") is None


def test_reproducible_env_sets_tex_timestamps(monkeypatch) -> None:
    for key in REPRODUCIBLE_TEX_ENV:
        monkeypatch.delenv(key, raising=False)

    env = _reproducible_env()

    assert env["SOURCE_DATE_EPOCH"] == "1767225600"
    assert env["FORCE_SOURCE_DATE"] == "1"


def test_clean_latex_state_removes_auxiliary_files(tmp_path: Path) -> None:
    tex = tmp_path / "main.tex"
    pdf = tmp_path / "main.pdf"
    tex.write_text("source", encoding="utf-8")
    pdf.write_text("pdf", encoding="utf-8")
    for extension in STALE_LATEX_EXTENSIONS:
        (tmp_path / f"main{extension}").write_text("stale", encoding="utf-8")

    _clean_latex_state(tmp_path, "main")

    assert tex.exists()
    assert pdf.exists()
    assert not any((tmp_path / f"main{extension}").exists() for extension in STALE_LATEX_EXTENSIONS)
