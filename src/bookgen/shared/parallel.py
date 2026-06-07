"""Small parallel-processing helpers (guideline 15).

Two complementary primitives:

* ``parallel_map`` uses a thread pool — correct for I/O-bound work (file writes,
  figure rendering via the thread-safe OO matplotlib API, network calls behind the
  gatekeeper) where the GIL is released during the blocking call.
* ``cpu_parallel_map`` uses a process pool — correct for CPU-bound work that would
  otherwise be serialized by the GIL.

Order is preserved: results line up with ``items``. Workers default to a modest,
machine-relative cap to avoid oversubscription.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def _resolve_workers(items: Sequence[T], max_workers: int | None) -> int:
    """Pick a worker count: explicit override, else min(items, cpu count)."""
    if max_workers is not None:
        return max(1, max_workers)
    return max(1, min(len(items) or 1, (os.cpu_count() or 2)))


def parallel_map(
    func: Callable[[T], R], items: Iterable[T], max_workers: int | None = None
) -> list[R]:
    """Apply ``func`` to each item across threads (I/O-bound), preserving order."""
    materialized = list(items)
    if len(materialized) <= 1:
        return [func(item) for item in materialized]
    with ThreadPoolExecutor(max_workers=_resolve_workers(materialized, max_workers)) as pool:
        return list(pool.map(func, materialized))


def cpu_parallel_map(
    func: Callable[[T], R], items: Iterable[T], max_workers: int | None = None
) -> list[R]:
    """Apply ``func`` to each item across processes (CPU-bound), preserving order."""
    materialized = list(items)
    if len(materialized) <= 1:
        return [func(item) for item in materialized]
    with ProcessPoolExecutor(max_workers=_resolve_workers(materialized, max_workers)) as pool:
        return list(pool.map(func, materialized))
