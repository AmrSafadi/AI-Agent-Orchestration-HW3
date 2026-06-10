"""Tests for LaTeX build-log analysis (scan_log_issues, pdf_page_count)."""

from __future__ import annotations

from bookgen.latex.compiler_log import pdf_page_count, scan_log_issues


def test_scan_log_issues_flags_errors_and_warnings() -> None:
    log = "! Undefined control sequence.\nOverfull \\hbox (5.0pt too wide)\n"
    issues = scan_log_issues(log)
    assert any("LaTeX error" in issue for issue in issues)
    assert any("overfull" in issue.lower() for issue in issues)


def test_scan_log_issues_clean_log_is_empty() -> None:
    assert scan_log_issues("This is a perfectly clean build log.\n") == []


def test_pdf_page_count_extracts_or_none() -> None:
    assert pdf_page_count("Output written on main.pdf (19 pages, 123456 bytes)") == 19
    assert pdf_page_count("no page information in this log") is None
