"""Tests for the CLI argument parser (the CLI delegates all logic to the SDK)."""

from __future__ import annotations

import pytest

from bookgen.main import build_parser


def test_parser_defaults_to_no_flags() -> None:
    args = build_parser().parse_args([])
    assert not args.run_crew
    assert not args.build_pdf


def test_parser_accepts_dry_run_and_build_pdf() -> None:
    args = build_parser().parse_args(["--dry-run", "--build-pdf"])
    assert args.dry_run
    assert args.build_pdf


def test_parser_accepts_run_crew() -> None:
    args = build_parser().parse_args(["--run-crew"])
    assert args.run_crew


def test_parser_accepts_estimate_cost() -> None:
    args = build_parser().parse_args(["--estimate-cost"])
    assert args.estimate_cost


def test_dry_run_and_run_crew_are_mutually_exclusive() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--dry-run", "--run-crew"])
