"""Deterministic harness components (citations, graph, assets, evidence).

Only the lightweight, dependency-free modules are re-exported here. ``assets``
and ``graph_generator`` pull in matplotlib, so they are imported on demand via
their full module path to keep the common import path (config/CLI) fast.
"""

from bookgen.harness import citation_report, citations, evidence

__all__ = ["citation_report", "citations", "evidence"]
