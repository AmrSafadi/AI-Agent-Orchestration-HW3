"""Tests for deterministic asset preparation."""

from __future__ import annotations

from pathlib import Path

from bookgen.harness.assets import (
    build_asset_specs,
    generate_image_asset,
    missing_asset_files,
)


def test_build_asset_specs_covers_all_required_kinds() -> None:
    kinds = {spec.kind for spec in build_asset_specs()}
    assert kinds == {"image", "graph", "table", "formula"}


def test_generate_image_asset_creates_non_empty_png(tmp_path: Path) -> None:
    out = generate_image_asset(tmp_path / "img.png")
    assert out.exists()
    assert out.stat().st_size > 0


def test_missing_asset_files_reports_absent(tmp_path: Path) -> None:
    specs = build_asset_specs()
    assert len(missing_asset_files(specs, root_dir=tmp_path)) == len(specs)
