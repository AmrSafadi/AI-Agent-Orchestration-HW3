"""Visualizations for the sensitivity analysis (guideline 9.3).

Every figure carries axis labels, a descriptive title, a legend where multiple
series are shown, a colorblind-safe palette, and high resolution. Figures render
concurrently through the thread-safe OO matplotlib helper (guideline 15).
"""

from __future__ import annotations

from pathlib import Path

from bookgen.harness._mpl import PALETTE, figure
from bookgen.research.sensitivity import (
    BASELINE,
    CHAPTERS_RANGE,
    WORDS_RANGE,
    estimate_pages,
    heatmap_grid,
    oat_sensitivity,
)
from bookgen.shared.parallel import parallel_map


def generate_figures(output_dir: Path | str = "generated/research") -> list[Path]:
    """Render every sensitivity figure concurrently and return their paths."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = oat_sensitivity()
    builders = [
        lambda: _plot_oat(results, out / "oat_lines.png"),
        lambda: _plot_bars(results, out / "sensitivity_bars.png"),
        lambda: _plot_scatter(results, out / "complexity_scatter.png"),
        lambda: _plot_box(results, out / "pages_boxplot.png"),
        lambda: _plot_heatmap(out / "pages_heatmap.png"),
        lambda: _plot_waterfall(out / "waterfall.png"),
    ]
    return parallel_map(lambda build: build(), builders)


def _plot_oat(results: dict, path: Path) -> Path:
    """Line chart of estimated pages vs each parameter's normalized sweep position.

    The three parameters span very different raw ranges (chapters 3-10, sections
    2-6, words 150-450), so plotting them on a shared *raw* x-axis would visually
    distort the comparison (the wide ``words`` range would dominate). We map each
    sweep onto its 0-1 fraction (min -> max) so the curves are directly
    comparable: the steepest line has the largest total effect across its sweep
    (here ``sections``), matching the partial-derivative ranking.
    """
    with figure(path, (7, 4)) as ax:
        for index, (param, series) in enumerate(results.items()):
            values = [v for v, _ in series]
            low, high = min(values), max(values)
            span = (high - low) or 1
            fractions = [(value - low) / span for value in values]
            ax.plot(
                fractions,
                [p for _, p in series],
                marker="o",
                color=PALETTE[index],
                label=param,
            )
        ax.set_xlabel("fraction of parameter sweep (min -> max)")
        ax.set_ylabel("estimated pages")
        ax.set_title("OAT sensitivity (normalized parameter sweep)")
        ax.legend(title="parameter")
    return path


def _plot_bars(results: dict, path: Path) -> Path:
    """Bar chart of each parameter's page-count range (sensitivity magnitude)."""
    deltas = {p: max(v for _, v in s) - min(v for _, v in s) for p, s in results.items()}
    with figure(path, (6, 4)) as ax:
        for index, (param, value) in enumerate(deltas.items()):
            ax.bar(param, value, color=PALETTE[index], label=param)
        ax.set_ylabel("page-count range across sweep")
        ax.set_title("Sensitivity magnitude by parameter")
        ax.legend(title="parameter")
    return path


def _plot_scatter(results: dict, path: Path) -> Path:
    """Scatter of estimated pages against swept parameter values."""
    with figure(path, (6, 4)) as ax:
        for index, (param, series) in enumerate(results.items()):
            ax.scatter(
                [v for v, _ in series],
                [p for _, p in series],
                color=PALETTE[index],
                alpha=0.75,
                label=param,
            )
        ax.set_xlabel("swept parameter value")
        ax.set_ylabel("estimated pages")
        ax.set_title("Estimated pages vs swept parameter value")
        ax.legend(title="parameter")
    return path


def _plot_box(results: dict, path: Path) -> Path:
    """Box plot of the page-count distribution per swept parameter."""
    labels = list(results)
    data = [[pages for _, pages in results[label]] for label in labels]
    with figure(path, (6, 4)) as ax:
        ax.boxplot(data)
        ax.set_xticks(range(1, len(labels) + 1))
        ax.set_xticklabels(labels)
        ax.set_ylabel("estimated pages")
        ax.set_title("Page-count distribution per swept parameter")
    return path


def _plot_heatmap(path: Path) -> Path:
    """Heatmap of estimated pages over (chapters x words-per-section)."""
    grid = heatmap_grid()
    with figure(path, (7, 4)) as ax:
        image = ax.imshow(grid, aspect="auto", origin="lower", cmap="cividis")
        ax.set_xticks(range(len(CHAPTERS_RANGE)))
        ax.set_xticklabels(CHAPTERS_RANGE)
        ax.set_yticks(range(len(WORDS_RANGE)))
        ax.set_yticklabels(WORDS_RANGE)
        ax.set_xlabel("chapters")
        ax.set_ylabel("words per section")
        ax.set_title("Estimated pages: chapters x words/section")
        ax.figure.colorbar(image, ax=ax, label="estimated pages")
    return path


def _plot_waterfall(path: Path) -> Path:
    """Waterfall of cumulative page contribution by parameter (variance view)."""
    start = estimate_pages(3, 2, 150)
    chapters = estimate_pages(BASELINE["chapters"], 2, 150)
    sections = estimate_pages(BASELINE["chapters"], BASELINE["sections"], 150)
    steps = [
        ("base", start, 0),
        ("chapters", chapters - start, start),
        ("sections", sections - chapters, chapters),
        ("words", estimate_pages(**BASELINE) - sections, sections),
    ]
    with figure(path, (7, 4)) as ax:
        for index, (label, value, bottom) in enumerate(steps):
            ax.bar(label, value, bottom=bottom, color=PALETTE[index])
        ax.set_ylabel("estimated pages")
        ax.set_title("Waterfall: cumulative page contribution by parameter")
    return path
