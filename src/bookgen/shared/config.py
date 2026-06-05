"""Configuration loading and validation for BookGen.

The Pydantic models live in ``config_models`` and are re-exported here so callers
can keep importing them from ``bookgen.shared.config``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bookgen.shared.config_models import (
    AppConfig,
    BudgetsConfig,
    LanguageSupportConfig,
    LatexConfig,
    ModelsConfig,
    PathConfig,
    ProjectMetadata,
    RateLimitsConfig,
    SetupConfig,
    WorkflowConfig,
)

__all__ = [
    "REQUIRED_CONFIG_FILES",
    "EXPECTED_CONFIG_VERSION",
    "AppConfig",
    "BudgetsConfig",
    "LanguageSupportConfig",
    "LatexConfig",
    "ModelsConfig",
    "PathConfig",
    "ProjectMetadata",
    "RateLimitsConfig",
    "SetupConfig",
    "WorkflowConfig",
    "project_root",
    "load_json_file",
    "load_config",
    "_validate_config_versions",
]

REQUIRED_CONFIG_FILES = {
    "setup": "setup.json",
    "models": "models.json",
    "latex": "latex.json",
    "budgets": "budgets.json",
    "rate_limits": "rate_limits.json",
}

EXPECTED_CONFIG_VERSION = "1.00"


def project_root() -> Path:
    """Return the repository root inferred from this module location."""
    return Path(__file__).resolve().parents[3]


def load_json_file(path: Path) -> dict[str, Any]:
    """Load a JSON object from disk."""
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object: {path}")
    return data


def load_config(config_dir: Path | None = None) -> AppConfig:
    """Load and validate all required configuration files."""
    root = project_root()
    resolved_config_dir = config_dir or root / "config"

    raw = {
        key: load_json_file(resolved_config_dir / filename)
        for key, filename in REQUIRED_CONFIG_FILES.items()
    }
    config = AppConfig(
        setup=SetupConfig.model_validate(raw["setup"]),
        models=ModelsConfig.model_validate(raw["models"]),
        latex=LatexConfig.model_validate(raw["latex"]),
        budgets=BudgetsConfig.model_validate(raw["budgets"]),
        rate_limits=RateLimitsConfig.model_validate(raw["rate_limits"]),
        root_dir=root,
        config_dir=resolved_config_dir,
    )
    _validate_config_versions(config)
    return config


def _validate_config_versions(config: AppConfig) -> None:
    """Fail if any versioned config file does not match the expected version."""
    actual = {
        "models": config.models.version,
        "latex": config.latex.version,
        "budgets": config.budgets.version,
        "rate_limits": config.rate_limits.version,
    }
    mismatched = {name: value for name, value in actual.items() if value != EXPECTED_CONFIG_VERSION}
    if mismatched:
        raise ValueError(
            f"config version mismatch (expected {EXPECTED_CONFIG_VERSION}): {mismatched}"
        )
