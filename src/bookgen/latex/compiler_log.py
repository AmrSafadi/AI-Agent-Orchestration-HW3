"""Pure-text analysis of LaTeX build logs (warnings, errors, page count).

Split out of ``compiler`` (guideline 3.2) so the process-running and
log-parsing concerns live in separate files. This module has no dependency on
``compiler``, so re-importing it back there introduces no import cycle.
"""

from __future__ import annotations

import re


def scan_log_issues(log_text: str) -> list[str]:
    """Return human-readable warnings/errors detected in a LaTeX build log."""
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
    # TeX prefixes hard errors with "! " (polyglossia/LaTeX errors, undefined
    # control sequences); never report these as a clean build.
    for message in dict.fromkeys(re.findall(r"^!\s?.+", log_text, flags=re.MULTILINE)):
        issues.append(f"LaTeX error: {message.strip()[:140]}")
    return issues


def pdf_page_count(log_text: str) -> int | None:
    """Extract the page count reported by the engine, if present."""
    match = re.search(r"Output written on \S+\.pdf \((\d+) page", log_text)
    return int(match.group(1)) if match else None
