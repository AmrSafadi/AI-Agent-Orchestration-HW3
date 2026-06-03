"""Configuration loading and validation for BookGen."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

REQUIRED_CONFIG_FILES = {
    "setup": "setup.json",
    "models": "models.json",
    "latex": "latex.json",
    "budgets": "budgets.json",
}

REQUIRED_AGENTS = ("planner", "research", "writer", "reviewer", "latex")


class ProjectMetadata(BaseModel):
    """Project identity shown in the CLI and generated document."""

    name: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    author: str = Field(min_length=1)
    course: str = Field(min_length=1)
    version: str = Field(min_length=1)


class WorkflowConfig(BaseModel):
    """CrewAI workflow configuration."""

    process: Literal["sequential"]
    agents: list[str] = Field(min_length=1)

    @field_validator("agents")
    @classmethod
    def require_expected_agents(cls, value: list[str]) -> list[str]:
        missing = [agent for agent in REQUIRED_AGENTS if agent not in value]
        if missing:
            raise ValueError(f"missing required agents: {', '.join(missing)}")
        return value


class PathConfig(BaseModel):
    """Project-relative paths used by later milestones."""

    intermediate_dir: str = Field(min_length=1)
    generated_dir: str = Field(min_length=1)
    template_dir: str = Field(min_length=1)


class SetupConfig(BaseModel):
    """Top-level setup configuration."""

    project: ProjectMetadata
    workflow: WorkflowConfig
    paths: PathConfig


class ModelsConfig(BaseModel):
    """Model defaults for future CrewAI agents."""

    default_provider: str = Field(min_length=1)
    default_model: str = Field(min_length=1)
    temperature: float = Field(ge=0, le=2)
    agent_models: dict[str, str] = Field(min_length=1)

    @field_validator("agent_models")
    @classmethod
    def require_agent_models(cls, value: dict[str, str]) -> dict[str, str]:
        missing = [agent for agent in REQUIRED_AGENTS if agent not in value]
        if missing:
            raise ValueError(f"missing model mapping for agents: {', '.join(missing)}")
        return value


class LanguageSupportConfig(BaseModel):
    """Language settings for the future LaTeX renderer."""

    primary: str = Field(min_length=1)
    secondary: str = Field(min_length=1)
    bidi_required: bool


class LatexConfig(BaseModel):
    """LaTeX build settings."""

    engine: str = Field(min_length=1)
    fallback_engine: str = Field(min_length=1)
    bibliography_backend: str = Field(min_length=1)
    main_template: str = Field(min_length=1)
    output_pdf: str = Field(min_length=1)
    passes: int = Field(ge=1)
    language_support: LanguageSupportConfig


class BudgetsConfig(BaseModel):
    """Cost and token budget placeholders for future API usage."""

    max_total_usd: float = Field(ge=0)
    max_total_tokens: int = Field(ge=0)
    warn_at_percent: int = Field(ge=1, le=100)
    notes: str = ""


class AppConfig(BaseModel):
    """Validated application configuration loaded from config files."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    setup: SetupConfig
    models: ModelsConfig
    latex: LatexConfig
    budgets: BudgetsConfig
    root_dir: Path
    config_dir: Path

    @property
    def output_dir(self) -> Path:
        """Return the configured generated output directory."""
        return self.root_dir / self.setup.paths.generated_dir


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
    return AppConfig(
        setup=SetupConfig.model_validate(raw["setup"]),
        models=ModelsConfig.model_validate(raw["models"]),
        latex=LatexConfig.model_validate(raw["latex"]),
        budgets=BudgetsConfig.model_validate(raw["budgets"]),
        root_dir=root,
        config_dir=resolved_config_dir,
    )
