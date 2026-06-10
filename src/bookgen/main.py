"""Command-line entry point for the book generation project.

The CLI holds no business logic; it parses arguments and delegates to the SDK.
"""

from __future__ import annotations

import argparse

from pydantic import ValidationError

from bookgen.sdk import BookGenSDK
from bookgen.shared.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description="BookGen CrewAI article/book generator.")
    execution_group = parser.add_mutually_exclusive_group()
    execution_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the safe dry-run path. This is the default and never calls CrewAI kickoff.",
    )
    execution_group.add_argument(
        "--run-crew",
        action="store_true",
        help="Run real CrewAI execution. Requires OPENAI_API_KEY and may call the model provider.",
    )
    parser.add_argument(
        "--build-pdf",
        action="store_true",
        help="After rendering main.tex, attempt LaTeX compilation (requires a TeX toolchain).",
    )
    parser.add_argument(
        "--estimate-cost",
        action="store_true",
        help="Print a config-driven token/USD cost forecast for a real run, then exit (no API call).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and drive the BookGen SDK."""
    args = build_parser().parse_args(argv)
    logger = configure_logging()

    try:
        sdk = BookGenSDK()
    except (FileNotFoundError, ValueError, ValidationError) as exc:
        logger.error("Configuration failed: %s", exc)
        return 1

    project = sdk.config.setup.project
    print("BookGen configuration loaded successfully.")
    print(f"Project title: {project.name}")
    print(f"Topic: {project.topic}")
    print(f"Output directory: {sdk.config.output_dir}")

    if args.estimate_cost:
        sdk.run_crew(dry_run=True)  # produce the manuscript artifact used for sizing
        forecast = sdk.estimate_cost()
        print(
            f"Cost forecast (model={forecast['model']}): "
            f"~{forecast['input_tokens']} input + {forecast['output_tokens']} output tokens "
            f"=> ~${forecast['estimated_usd']} (no API call)."
        )
        return 0

    dry_run = not args.run_crew
    print("Execution mode: " + ("DRY-RUN (default)." if dry_run else "REAL CREWAI RUN."))

    try:
        result = sdk.generate_book(dry_run=dry_run, build_pdf=args.build_pdf)
    except (RuntimeError, FileNotFoundError) as exc:
        logger.error("%s", exc)
        return 1

    print(f"Rendered LaTeX project: {result['main_tex']}")
    print(result["message"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
