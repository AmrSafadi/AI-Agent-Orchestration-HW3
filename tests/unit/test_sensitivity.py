"""Tests for the deterministic sensitivity analysis and its visualizations."""

from __future__ import annotations

from pathlib import Path

from bookgen.research.sensitivity import (
    compare_baselines,
    estimate_pages,
    heatmap_grid,
    oat_sensitivity,
    partial_sensitivity,
)
from bookgen.research.sensitivity_plots import generate_figures


def test_estimate_pages_increases_with_size() -> None:
    assert estimate_pages(6, 3, 250) > estimate_pages(3, 3, 250)
    assert estimate_pages(6, 3, 250) >= 4  # always above front matter


def test_oat_sensitivity_structure() -> None:
    results = oat_sensitivity()
    assert set(results) == {"chapters", "sections", "words"}
    assert all(len(series) >= 2 for series in results.values())


def test_partial_sensitivity_is_positive() -> None:
    partials = partial_sensitivity()
    assert set(partials) == {"chapters", "sections", "words"}
    assert all(value > 0 for value in partials.values())


def test_compare_baselines_orders_by_size() -> None:
    comparison = compare_baselines()
    assert comparison["lean"] < comparison["baseline"] < comparison["rich"]


def test_heatmap_grid_is_rectangular() -> None:
    grid = heatmap_grid()
    assert len(grid) >= 2
    assert len({len(row) for row in grid}) == 1  # all rows same width


def test_generate_figures_creates_all_types(tmp_path: Path) -> None:
    paths = generate_figures(tmp_path)
    assert len(paths) == 6  # line, bar, scatter, box, heatmap, waterfall
    assert all(path.exists() and path.stat().st_size > 0 for path in paths)
