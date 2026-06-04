from pathlib import Path

import pytest

from bookgen.shared.config import (
    EXPECTED_CONFIG_VERSION,
    _validate_config_versions,
    load_config,
)


def test_load_config_from_project_config_dir() -> None:
    config = load_config(Path("config"))
    assert config.setup.project.name == "AI Agent Orchestration HW3"
    assert config.setup.workflow.process == "sequential"
    assert config.latex.engine == "lualatex"
    assert config.output_dir.name == "generated"


def test_config_versions_match_expected() -> None:
    config = load_config(Path("config"))
    assert config.models.version == EXPECTED_CONFIG_VERSION
    assert config.rate_limits.version == EXPECTED_CONFIG_VERSION


def test_config_version_mismatch_raises() -> None:
    config = load_config(Path("config"))
    config.models.version = "9.99"
    with pytest.raises(ValueError, match="version mismatch"):
        _validate_config_versions(config)
