from pathlib import Path

from bookgen.shared.config import load_config


def test_load_config_from_project_config_dir() -> None:
    config = load_config(Path("config"))

    assert config.setup.project.name == "AI Agent Orchestration HW3"
    assert config.setup.workflow.process == "sequential"
    assert config.latex.engine == "lualatex"
    assert config.output_dir.name == "generated"
