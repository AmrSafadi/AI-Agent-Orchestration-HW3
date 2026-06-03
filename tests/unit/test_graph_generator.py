from pathlib import Path

from bookgen.harness.graph_generator import generate_agent_pipeline_graph


def test_graph_generation_creates_png(tmp_path: Path) -> None:
    output_path = tmp_path / "agent_pipeline_graph.png"

    generated_path = generate_agent_pipeline_graph(output_path)

    assert generated_path == output_path
    assert output_path.exists()
    assert output_path.read_bytes().startswith(b"\x89PNG")
