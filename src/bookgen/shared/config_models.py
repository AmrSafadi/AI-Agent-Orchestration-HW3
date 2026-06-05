"""Pydantic configuration models for BookGen.

Separated from the loader (``config.py``) so each module stays focused and within
the 150-line-per-file limit. ``config.py`` re-exports these, so callers may keep
importing them from ``bookgen.shared.config``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from bookgen.shared.constants import REQUIRED_AGENTS


class ProjectMetadata(BaseModel):
    """Project identity shown in the CLI and generated document."""

    name: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    author: str = Field(min_length=1)
    course: str = Field(min_length=1)
    lecturer: str = Field(min_length=1)
    date: str = Field(min_length=1)
    version: str = Field(min_length=1)


class WorkflowConfig(BaseModel):
    """CrewAI workflow configuration."""

    process: Literal["sequential"]
    agents: list[str] = Field(min_length=1)

    @field_validator("agents")
    @classmethod
    def require_expected_agents(cls, value: list[str]) -> list[str]:
        """Ensure every required agent role is present in the workflow."""
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
    """Model defaults for the CrewAI agents."""

    version: str = Field(min_length=1)
    default_provider: str = Field(min_length=1)
    default_model: str = Field(min_length=1)
    temperature: float = Field(ge=0, le=2)
    agent_models: dict[str, str] = Field(min_length=1)

    @field_validator("agent_models")
    @classmethod
    def require_agent_models(cls, value: dict[str, str]) -> dict[str, str]:
        """Ensure every required agent has a model mapping."""
        missing = [agent for agent in REQUIRED_AGENTS if agent not in value]
        if missing:
            raise ValueError(f"missing model mapping for agents: {', '.join(missing)}")
        return value


class LanguageSupportConfig(BaseModel):
    """Language settings for the LaTeX renderer."""

    primary: str = Field(min_length=1)
    secondary: str = Field(min_length=1)
    bidi_required: bool


class LatexConfig(BaseModel):
    """LaTeX build settings."""

    version: str = Field(min_length=1)
    engine: str = Field(min_length=1)
    fallback_engine: str = Field(min_length=1)
    bibliography_backend: str = Field(min_length=1)
    main_template: str = Field(min_length=1)
    output_pdf: str = Field(min_length=1)
    passes: int = Field(ge=1)
    language_support: LanguageSupportConfig


class BudgetsConfig(BaseModel):
    """Cost and token budget placeholders for API usage."""

    version: str = Field(min_length=1)
    max_total_usd: float = Field(ge=0)
    max_total_tokens: int = Field(ge=0)
    warn_at_percent: int = Field(ge=1, le=100)
    notes: str = ""


class RateLimitsConfig(BaseModel):
    """API rate-limit configuration for the gatekeeper (guideline 5.2)."""

    version: str = Field(min_length=1)
    requests_per_minute: int = Field(gt=0)
    requests_per_hour: int = Field(gt=0)
    concurrent_max: int = Field(gt=0)
    retry_after_seconds: float = Field(ge=0)
    max_retries: int = Field(ge=0)
    max_queue_depth: int = Field(gt=0)


class AppConfig(BaseModel):
    """Validated application configuration loaded from config files."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    setup: SetupConfig
    models: ModelsConfig
    latex: LatexConfig
    budgets: BudgetsConfig
    rate_limits: RateLimitsConfig
    root_dir: Path
    config_dir: Path

    @property
    def output_dir(self) -> Path:
        """Return the configured generated output directory."""
        return self.root_dir / self.setup.paths.generated_dir
