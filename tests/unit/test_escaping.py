"""Tests for LaTeX special-character escaping."""

from __future__ import annotations

from bookgen.latex.escaping import escape_latex


def test_escapes_all_special_characters() -> None:
    expected = (
        r"\&\%\$\#\_\{\}"
        r"\textasciitilde{}"
        r"\textasciicircum{}"
        r"\textbackslash{}"
    )
    assert escape_latex("&%$#_{}~^\\") == expected


def test_plain_text_is_unchanged() -> None:
    assert escape_latex("Hello World 123") == "Hello World 123"


def test_backslash_does_not_double_escape() -> None:
    assert escape_latex("a\\b") == r"a\textbackslash{}b"
