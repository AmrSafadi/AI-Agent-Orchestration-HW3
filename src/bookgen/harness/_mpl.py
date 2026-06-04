"""Matplotlib configured for headless, deterministic (Agg) figure generation.

Importing pyplot directly can select an interactive backend (e.g. TkAgg), which
fails on headless machines. Routing every figure module through this helper
forces the non-interactive Agg backend before pyplot is imported.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (backend must be set before pyplot import)

__all__ = ["plt"]
