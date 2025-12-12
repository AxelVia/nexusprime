"""Tests for configuration module."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from nexusprime.config import Settings


class TestSettings:
    """Test cases for Settings."""
    
    def test_settings_with_valid_env(self, mock_env_vars):
        """Test settings creation with valid environment variables."""
        settings = Settings()
        assert settings.google_api_key == "test_api_key"
        assert settings.github_token == "test_github_token"
    
    def test_settings_missing_required_env(self, monkeypatch):
        """Test that missing required env variables raise error."""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        
        with pytest.raises(ValidationError):
            Settings()
    
    def test_settings_defaults(self, mock_env_vars):
        """Test default values."""
        settings = Settings()
        assert settings.llm_model == "gemini-2.5-pro"
        assert settings.llm_temperature == 0.2
        assert settings.max_feedback_loops == 5
        assert settings.dev_quality_threshold == 75
        assert settings.prod_quality_threshold == 95
    
    def test_settings_custom_values(self, mock_env_vars, monkeypatch):
        """Test custom values override defaults."""
        monkeypatch.setenv("LLM_MODEL", "gemini-pro")
        monkeypatch.setenv("LLM_TEMPERATURE", "0.5")
        
        settings = Settings()
        assert settings.llm_model == "gemini-pro"
        assert settings.llm_temperature == 0.5
