"""LaTeX escaping for untrusted, agent-authored text.

A single-pass regex substitution prevents re-escaping (e.g. the braces produced
when escaping a backslash are not themselves escaped again).
"""

from __future__ import annotations

import re

_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

_PATTERN = re.compile("|".join(re.escape(character) for character in _REPLACEMENTS))


def escape_latex(text: str) -> str:
    """Escape LaTeX special characters in plain text for safe insertion."""
    return _PATTERN.sub(lambda match: _REPLACEMENTS[match.group()], text)
