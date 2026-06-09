"""Deterministic asset preparation (image, graph, table, formula specs)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from bookgen.document.report_schemas import AssetSpec
from bookgen.harness._mpl import figure

DEFAULT_IMAGE_PATH = Path("generated/assets/images/course_concept_image.png")

REQUIRED_ASSETS: tuple[AssetSpec, ...] = (
    AssetSpec(
        asset_id="course_concept_image",
        kind="image",
        source="matplotlib",
        output_path=str(DEFAULT_IMAGE_PATH),
        caption="Football pitch zones used for chance creation analysis.",
    ),
    AssetSpec(
        asset_id="agent_pipeline_graph",
        kind="graph",
        source="matplotlib",
        output_path="generated/assets/graphs/agent_pipeline_graph.png",
        caption="Football analytics workflow from match events to coaching action.",
    ),
    AssetSpec(
        asset_id="agent_roles_table",
        kind="table",
        source="latex",
        output_path="generated/latex/agent_roles_table.tex",
        caption="Core football analytics metrics and tactical meaning.",
    ),
    AssetSpec(
        asset_id="quality_score_formula",
        kind="formula",
        source="latex",
        output_path="generated/latex/quality_score_formula.tex",
        caption="Simplified expected-goals score for a shot.",
    ),
)


def build_asset_specs() -> list[AssetSpec]:
    """Return the specifications for every required document asset."""
    return list(REQUIRED_ASSETS)


def generate_image_asset(output_path: Path | str = DEFAULT_IMAGE_PATH) -> Path:
    """Generate a simple deterministic image asset and return its path."""
    path = Path(output_path)
    with figure(path, (6, 3.2), dpi=160) as ax:
        ax.set_facecolor("#2f7d46")
        ax.set_xlim(0, 105)
        ax.set_ylim(0, 68)
        ax.axis("off")
        line = {"color": "white", "linewidth": 2.0, "alpha": 0.95}
        ax.add_patch(plt.Rectangle((0, 0), 105, 68, fill=False, **line))
        ax.plot([52.5, 52.5], [0, 68], **line)
        ax.add_patch(plt.Circle((52.5, 34), 9.15, fill=False, **line))
        ax.add_patch(plt.Rectangle((0, 13.84), 16.5, 40.32, fill=False, **line))
        ax.add_patch(plt.Rectangle((88.5, 13.84), 16.5, 40.32, fill=False, **line))
        ax.add_patch(plt.Rectangle((0, 24.84), 5.5, 18.32, fill=False, **line))
        ax.add_patch(plt.Rectangle((99.5, 24.84), 5.5, 18.32, fill=False, **line))
        ax.scatter([82, 90, 74, 64], [34, 44, 24, 36], s=[260, 180, 130, 90], color="#ffd166")
        ax.annotate(
            "",
            xy=(90, 44),
            xytext=(82, 34),
            arrowprops={"arrowstyle": "->", "lw": 2.2, "color": "#073b4c"},
        )
        ax.annotate(
            "",
            xy=(74, 24),
            xytext=(82, 34),
            arrowprops={"arrowstyle": "->", "lw": 2.2, "color": "#073b4c"},
        )
        ax.text(
            0.5,
            0.08,
            "Chance Creation Zones",
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold",
            color="white",
            transform=ax.transAxes,
        )
        ax.text(82, 30, "xG hotspot", ha="center", va="center", fontsize=10, color="#073b4c")
    return path


def missing_asset_files(specs: list[AssetSpec], root_dir: Path | str = ".") -> list[str]:
    """Return the asset ids whose target files do not yet exist on disk."""
    root = Path(root_dir)
    return [spec.asset_id for spec in specs if not (root / spec.output_path).exists()]
