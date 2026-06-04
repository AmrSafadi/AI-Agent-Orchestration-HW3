"""SDK facade: the single entry point for all BookGen business logic.

Submission guideline 4.1 requires every business function to be reachable through
one SDK layer, so external consumers (CLI, services, tests) call this class
instead of importing internal modules directly.
"""

from __future__ import annotations

from typing import Any

from bookgen.latex.build import build_document as _build_document
from bookgen.orchestration.crew import run_crew as _run_crew
from bookgen.shared.config import AppConfig, load_config


class BookGenSDK:
    """The single public entry point for the BookGen pipeline."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self._config = config or load_config()

    @property
    def config(self) -> AppConfig:
        """Return the loaded, validated application configuration."""
        return self._config

    def run_crew(self, dry_run: bool = True) -> Any:
        """Run the crew. Dry-run is the default; a real run needs OPENAI_API_KEY."""
        return _run_crew(dry_run=dry_run, root_dir=self._config.root_dir)

    def generate_assets(self) -> dict[str, str]:
        """Generate the Python pipeline graph and the image asset."""
        from bookgen.harness.assets import generate_image_asset
        from bookgen.harness.graph_generator import generate_agent_pipeline_graph

        return {
            "graph": str(generate_agent_pipeline_graph()),
            "image": str(generate_image_asset()),
        }

    def build_document(self, compile_after: bool = False) -> dict:
        """Render ``main.tex`` from the generated artifacts (optionally compile)."""
        project = self._config.setup.project
        metadata = {
            "author": project.author,
            "course": project.course,
            "lecturer": project.lecturer,
            "date": project.date,
        }
        return _build_document(
            self._config.root_dir,
            metadata,
            compile_after=compile_after,
            latex_config=self._config.latex.model_dump(),
        )

    def generate_book(self, dry_run: bool = True, build_pdf: bool = False) -> dict:
        """Run the full pipeline: crew -> assets -> rendered document (-> PDF)."""
        self.run_crew(dry_run=dry_run)
        self.generate_assets()
        return self.build_document(compile_after=build_pdf)
