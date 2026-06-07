"""Deterministic parameter sensitivity analysis for the document pipeline.

Estimates document length from structural parameters and runs a one-at-a-time
(OAT) sensitivity study plus a finite-difference (partial-derivative) sensitivity
index (guideline 9). Visualizations live in ``sensitivity_plots``.

Page model:  P_hat = ceil(chapters * sections * words / WORDS_PER_PAGE) + FRONT_MATTER
"""

from __future__ import annotations

import math

WORDS_PER_PAGE = 450
FRONT_MATTER_PAGES = 3  # cover + table of contents + figures/table/formula
BASELINE = {"chapters": 6, "sections": 3, "words": 250}
CHAPTERS_RANGE = list(range(3, 11))
WORDS_RANGE = list(range(150, 451, 50))

# Alternative configurations compared in the analysis notebook (guideline 9.2).
ALTERNATIVES = {
    "lean": {"chapters": 4, "sections": 2, "words": 200},
    "baseline": BASELINE,
    "rich": {"chapters": 8, "sections": 4, "words": 350},
}


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


def partial_sensitivity(step: int = 1) -> dict[str, float]:
    """Finite-difference partial derivative of pages w.r.t. each parameter at baseline."""
    sensitivities: dict[str, float] = {}
    for param, value in BASELINE.items():
        high = estimate_pages(**{**BASELINE, param: value + step})
        low = estimate_pages(**{**BASELINE, param: max(value - step, 1)})
        sensitivities[param] = (high - low) / (2 * step)
    return sensitivities


def heatmap_grid(sections: int = 3) -> list[list[int]]:
    """Build a 2D grid of page estimates over (words/section x chapters)."""
    return [[estimate_pages(c, sections, w) for c in CHAPTERS_RANGE] for w in WORDS_RANGE]


def compare_baselines() -> dict[str, int]:
    """Estimate pages for the lean / baseline / rich configurations."""
    return {name: estimate_pages(**params) for name, params in ALTERNATIVES.items()}
