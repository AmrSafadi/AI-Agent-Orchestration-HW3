"""Tests for the parallel-processing helpers (order preserved, thread-safe)."""

from __future__ import annotations

import threading

from bookgen.shared.parallel import parallel_map


def test_parallel_map_preserves_order() -> None:
    assert parallel_map(lambda value: value * 2, [1, 2, 3, 4]) == [2, 4, 6, 8]


def test_parallel_map_single_item_runs_inline() -> None:
    assert parallel_map(lambda value: value + 1, [41]) == [42]


def test_parallel_map_runs_concurrently() -> None:
    seen_threads: set[int] = set()
    lock = threading.Lock()

    def record(value: int) -> int:
        with lock:
            seen_threads.add(threading.get_ident())
        return value

    parallel_map(record, list(range(8)), max_workers=4)
    assert len(seen_threads) > 1  # work actually spread across threads
