"""Centralized configuration for NexusPrime using Pydantic."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """NexusPrime configuration settings."""
    
    google_api_key: str
    github_token: str
    llm_model: str = "gemini-2.5-pro"
    llm_temperature: float = 0.2
    max_feedback_loops: int = 5
    dev_quality_threshold: int = 75
    prod_quality_threshold: int = 95
    workspace_dir: str = "workspace"
    memory_file: str = "nexus_memory.json"
    status_file: str = "status.json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get or create the global settings instance.
    
    Returns:
        Settings instance
    
    Raises:
        ValidationError: If required environment variables are missing
    """
    global settings
    if settings is None:
        settings = Settings()
    return settings
