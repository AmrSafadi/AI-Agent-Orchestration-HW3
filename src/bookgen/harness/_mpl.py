"""Headless, thread-safe matplotlib figure helpers.

Importing pyplot directly can select an interactive backend (e.g. TkAgg), which
fails on headless machines, and the pyplot state machine is not thread-safe. This
module forces the non-interactive Agg backend and exposes a ``figure`` context
manager built on the object-oriented ``Figure`` API so figures can be rendered
concurrently (guideline 15) and the create/save/close boilerplate lives in one
place (guideline 4.2, DRY).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (backend must be set before pyplot import)
from matplotlib.backends.backend_agg import FigureCanvasAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

# Colorblind-safe qualitative palette (Okabe-Ito).
PALETTE = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9")

__all__ = ["PALETTE", "figure", "plt"]


@contextmanager
def figure(
    path: Path | str, figsize: tuple[float, float] = (7, 4), dpi: int = 150
) -> Iterator[Any]:
    """Yield a fresh Axes, then save to ``path`` and release the figure.

    Uses the OO ``Figure`` API (no global pyplot state) so it is safe to call from
    multiple threads concurrently.
    """
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig = Figure(figsize=figsize)
    FigureCanvasAgg(fig)
    ax = fig.subplots()
    yield ax
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
