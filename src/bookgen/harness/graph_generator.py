"""Generate deterministic project graphs with matplotlib."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

DEFAULT_GRAPH_PATH = Path("generated/assets/graphs/agent_pipeline_graph.png")

PIPELINE_NODES = [
    "Planner",
    "Research",
    "Writer",
    "Reviewer",
    "LaTeX",
    "CitationManager",
    "Validator",
    "PDFCompiler",
]


def generate_agent_pipeline_graph(output_path: Path | str = DEFAULT_GRAPH_PATH) -> Path:
    """Generate the deterministic agent pipeline graph and return its path."""
    resolved_output_path = Path(output_path)
    resolved_output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(13, 3.8))
    ax.axis("off")

    y = 0

    for index, label in enumerate(PIPELINE_NODES):
        ax.text(
            index,
            y,
            label,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            bbox={
                "boxstyle": "round,pad=0.45",
                "facecolor": "#f6f8fb",
                "edgecolor": "#2f5f9f",
                "linewidth": 1.4,
            },
        )
        if index < len(PIPELINE_NODES) - 1:
            ax.annotate(
                "",
                xy=(index + 0.72, y),
                xytext=(index + 0.28, y),
                arrowprops={"arrowstyle": "->", "color": "#2f5f9f", "lw": 1.8},
            )

    ax.set_xlim(-0.6, len(PIPELINE_NODES) - 0.4)
    ax.set_ylim(-0.9, 0.9)
    ax.set_title("BookGen Sequential Agent and Harness Pipeline", fontsize=14, pad=18)

    fig.tight_layout()
    fig.savefig(resolved_output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    return resolved_output_path
