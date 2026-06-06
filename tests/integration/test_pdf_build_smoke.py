"""Smoke-test the real LaTeX PDF build when the local toolchain is available."""

from __future__ import annotations

from pathlib import Path

import pytest

from bookgen.latex.compiler import toolchain_available
from bookgen.sdk import BookGenSDK


@pytest.mark.skipif(
    not toolchain_available("lualatex", "biber"),
    reason="requires lualatex and biber on PATH",
)
def test_pdf_build_smoke_compiles_final_pdf() -> None:
    sdk = BookGenSDK()
    sdk.run_crew(dry_run=True)
    sdk.generate_assets()

    result = sdk.build_document(compile_after=True)

    assert result["compiled"] is True, result["message"]
    final_pdf = Path(result["final_pdf"])
    assert final_pdf.exists()
    assert final_pdf.stat().st_size > 1_000
    assert result["pages"] and result["pages"] >= 1
