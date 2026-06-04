"""Command-line entry point for the book generation project."""

from __future__ import annotations

import argparse

from pydantic import ValidationError

from bookgen.orchestration.crew import run_crew
from bookgen.shared.config import load_config
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
    return parser


def main(argv: list[str] | None = None) -> int:
    """Load configuration and run the selected execution mode."""
    args = build_parser().parse_args(argv)
    logger = configure_logging()

    try:
        app_config = load_config()
    except (FileNotFoundError, ValueError, ValidationError) as exc:
        logger.error("Configuration failed: %s", exc)
        return 1

    project = app_config.setup.project
    print("BookGen configuration loaded successfully.")
    print(f"Project title: {project.name}")
    print(f"Topic: {project.topic}")
    print(f"Output directory: {app_config.output_dir}")
    print(
        f"Artifact output directory: {app_config.root_dir / app_config.setup.paths.intermediate_dir}"
    )

    dry_run = not args.run_crew
    if dry_run:
        print("Execution mode: DRY-RUN (default). CrewAI kickoff will not be called.")
    else:
        print("Execution mode: REAL CREWAI RUN. OPENAI_API_KEY is required.")

    try:
        run_crew(dry_run=dry_run, root_dir=app_config.root_dir)
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 1

    print("PDF generation is not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
