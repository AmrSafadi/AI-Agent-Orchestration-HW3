"""Deterministic asset preparation (image, graph, table, formula specs)."""

from __future__ import annotations

from pathlib import Path

from bookgen.document.report_schemas import AssetSpec
from bookgen.harness._mpl import plt

DEFAULT_IMAGE_PATH = Path("generated/assets/images/course_concept_image.png")

REQUIRED_ASSETS: tuple[AssetSpec, ...] = (
    AssetSpec(
        asset_id="course_concept_image",
        kind="image",
        source="matplotlib",
        output_path=str(DEFAULT_IMAGE_PATH),
        caption="Conceptual illustration of agent orchestration.",
    ),
    AssetSpec(
        asset_id="agent_pipeline_graph",
        kind="graph",
        source="matplotlib",
        output_path="generated/assets/graphs/agent_pipeline_graph.png",
        caption="Sequential agent and deterministic harness pipeline.",
    ),
    AssetSpec(
        asset_id="agent_roles_table",
        kind="table",
        source="latex",
        output_path="generated/latex/tables/agent_roles_table.tex",
        caption="Responsibilities of each agent and deterministic component.",
    ),
    AssetSpec(
        asset_id="quality_score_formula",
        kind="formula",
        source="latex",
        output_path="generated/latex/formulas/quality_score_formula.tex",
        caption="Example weighted document quality score.",
    ),
)


def build_asset_specs() -> list[AssetSpec]:
    """Return the specifications for every required document asset."""
    return list(REQUIRED_ASSETS)


def generate_image_asset(output_path: Path | str = DEFAULT_IMAGE_PATH) -> Path:
    """Generate a simple deterministic image asset and return its path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 3.2))
    ax.axis("off")
    ax.text(
        0.5,
        0.5,
        "AI Agent Orchestration",
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
        color="#2f5f9f",
    )
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


def missing_asset_files(specs: list[AssetSpec], root_dir: Path | str = ".") -> list[str]:
    """Return the asset ids whose target files do not yet exist on disk."""
    root = Path(root_dir)
    return [spec.asset_id for spec in specs if not (root / spec.output_path).exists()]
