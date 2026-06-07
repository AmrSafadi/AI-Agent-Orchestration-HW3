"""Generate deterministic project graphs with matplotlib."""

from __future__ import annotations

from pathlib import Path

from bookgen.harness._mpl import figure

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
    y = 0
    with figure(resolved_output_path, (13, 3.8), dpi=180) as ax:
        ax.axis("off")
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

    return resolved_output_path
