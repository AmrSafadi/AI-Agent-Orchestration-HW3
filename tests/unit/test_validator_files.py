"""Tests for LaTeX-spec file-existence validation (T094, false-green guard)."""

from __future__ import annotations

import json
from pathlib import Path

from bookgen.document.validators import validate_latex_spec_files

_SPEC = {
    "title": "T",
    "engine": "lualatex",
    "main_template": "main.tex.j2",
    "output_pdf": "final.pdf",
    "chapter_files": ["c.tex"],
    "assets": [{"asset_id": "img", "kind": "image", "target_path": "assets/img.png"}],
    "bibliography_file": "refs.bib",
}


def test_latex_spec_files_missing_then_present(tmp_path: Path) -> None:
    spec = tmp_path / "latex_spec.json"
    spec.write_text(json.dumps(_SPEC), encoding="utf-8")

    report = validate_latex_spec_files(spec, root_dir=tmp_path)
    assert not report.passed

    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "img.png").write_text("x", encoding="utf-8")
    (tmp_path / "refs.bib").write_text("x", encoding="utf-8")

    report_after = validate_latex_spec_files(spec, root_dir=tmp_path)
    assert report_after.passed
