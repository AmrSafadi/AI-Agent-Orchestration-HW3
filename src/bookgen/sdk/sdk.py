"""SDK facade: the single entry point for all BookGen business logic.

Submission guideline 4.1 requires every business function to be reachable through
one SDK layer, so external consumers (CLI, services, tests) call this class
instead of importing internal modules directly.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bookgen.latex.build import build_document as _build_document
from bookgen.orchestration.crew import run_crew as _run_crew
from bookgen.shared.config import AppConfig, load_config

# Pipeline stages around which ``before_<stage>``/``after_<stage>`` hooks fire.
STAGES = ("run_crew", "generate_assets", "build_document")


class BookGenSDK:
    """The single public entry point for the BookGen pipeline."""

    def __init__(
        self,
        config: AppConfig | None = None,
        hooks: dict[str, list[Callable[..., Any]]] | None = None,
    ) -> None:
        self._config = config or load_config()
        # Extension points (guideline 12): map "before_<stage>"/"after_<stage>" to
        # lists of callables. before-hooks receive the SDK; after-hooks receive
        # the SDK and the stage result.
        self._hooks: dict[str, list[Callable[..., Any]]] = hooks or {}

    def _run_stage(self, name: str, run: Callable[[], Any]) -> Any:
        for hook in self._hooks.get(f"before_{name}", []):
            hook(self)
        result = run()
        for hook in self._hooks.get(f"after_{name}", []):
            hook(self, result)
        return result

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
        self._run_stage("run_crew", lambda: self.run_crew(dry_run=dry_run))
        self._run_stage("generate_assets", self.generate_assets)
        return self._run_stage(
            "build_document", lambda: self.build_document(compile_after=build_pdf)
        )

    def estimate_cost(self) -> dict[str, Any]:
        """Forecast token usage and USD cost for the current manuscript (no API)."""
        from bookgen.orchestration.accounting import estimate_cost_usd, estimate_tokens

        models = self._config.models
        manuscript = self._config.root_dir / "generated/intermediate/manuscript.md"
        text = manuscript.read_text(encoding="utf-8") if manuscript.exists() else ""
        output_tokens = estimate_tokens(text)
        input_tokens = output_tokens // 2  # prompt + retrieved context heuristic
        price = models.pricing.get(models.default_model)
        cost = estimate_cost_usd(input_tokens, output_tokens, price) if price else None
        return {
            "model": models.default_model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_usd": round(cost, 6) if cost is not None else None,
        }
