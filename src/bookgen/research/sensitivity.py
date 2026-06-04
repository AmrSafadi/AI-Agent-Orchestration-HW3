"""Deterministic parameter sensitivity analysis for the document pipeline.

Estimates document length from structural parameters and runs a one-at-a-time
(OAT) sensitivity study, producing data and visualizations (guideline 9:
parameter research, sensitivity analysis, and heatmaps/plots).

Page model:  P_hat = ceil(chapters * sections * words / WORDS_PER_PAGE) + FRONT_MATTER
"""

from __future__ import annotations

import math
from pathlib import Path

from bookgen.harness._mpl import plt

WORDS_PER_PAGE = 450
FRONT_MATTER_PAGES = 3  # cover + table of contents + figures/table/formula
BASELINE = {"chapters": 6, "sections": 3, "words": 250}
CHAPTERS_RANGE = list(range(3, 11))
WORDS_RANGE = list(range(150, 451, 50))


def estimate_pages(chapters: int, sections: int, words: int) -> int:
    """Estimate compiled page count from structural parameters."""
    body_pages = math.ceil(chapters * sections * words / WORDS_PER_PAGE)
    return body_pages + FRONT_MATTER_PAGES


def oat_sensitivity() -> dict[str, list[tuple[int, int]]]:
    """Run a one-at-a-time sensitivity sweep around the baseline."""
    ranges = {"chapters": CHAPTERS_RANGE, "sections": list(range(2, 7)), "words": WORDS_RANGE}
    results: dict[str, list[tuple[int, int]]] = {}
    for param, values in ranges.items():
        results[param] = [(value, estimate_pages(**{**BASELINE, param: value})) for value in values]
    return results


def heatmap_grid(sections: int = 3) -> list[list[int]]:
    """Build a 2D grid of page estimates over (words/section x chapters)."""
    return [[estimate_pages(c, sections, w) for c in CHAPTERS_RANGE] for w in WORDS_RANGE]


def generate_figures(output_dir: Path | str = "generated/research") -> list[Path]:
    """Generate the OAT line chart, the sensitivity bar chart, and the heatmap."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = oat_sensitivity()
    return [
        _plot_oat(results, out / "oat_lines.png"),
        _plot_bars(results, out / "sensitivity_bars.png"),
        _plot_scatter(results, out / "complexity_scatter.png"),
        _plot_box(results, out / "pages_boxplot.png"),
        _plot_heatmap(out / "pages_heatmap.png"),
    ]


def _plot_oat(results: dict, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4))
    for param, series in results.items():
        ax.plot([v for v, _ in series], [p for _, p in series], marker="o", label=param)
    ax.set_xlabel("parameter value")
    ax.set_ylabel("estimated pages")
    ax.set_title("OAT sensitivity of estimated page count")
    ax.legend()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _plot_bars(results: dict, path: Path) -> Path:
    deltas = {p: max(v for _, v in s) - min(v for _, v in s) for p, s in results.items()}
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(list(deltas), list(deltas.values()), color="#2f5f9f")
    ax.set_ylabel("page-count range across sweep")
    ax.set_title("Sensitivity magnitude by parameter")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _plot_scatter(results: dict, path: Path) -> Path:
    xs = [value for series in results.values() for value, _ in series]
    ys = [pages for series in results.values() for _, pages in series]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(xs, ys, color="#b4451f", alpha=0.7)
    ax.set_xlabel("swept parameter value")
    ax.set_ylabel("estimated pages")
    ax.set_title("Estimated pages vs swept parameter value")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _plot_box(results: dict, path: Path) -> Path:
    labels = list(results)
    data = [[pages for _, pages in results[label]] for label in labels]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.boxplot(data)
    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels)
    ax.set_ylabel("estimated pages")
    ax.set_title("Page-count distribution per swept parameter")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _plot_heatmap(path: Path) -> Path:
    grid = heatmap_grid()
    fig, ax = plt.subplots(figsize=(7, 4))
    image = ax.imshow(grid, aspect="auto", origin="lower", cmap="viridis")
    ax.set_xticks(range(len(CHAPTERS_RANGE)))
    ax.set_xticklabels(CHAPTERS_RANGE)
    ax.set_yticks(range(len(WORDS_RANGE)))
    ax.set_yticklabels(WORDS_RANGE)
    ax.set_xlabel("chapters")
    ax.set_ylabel("words per section")
    ax.set_title("Estimated pages: chapters x words/section")
    fig.colorbar(image, ax=ax, label="estimated pages")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path
