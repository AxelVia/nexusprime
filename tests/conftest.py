"""Pytest configuration and fixtures."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_memory_file(temp_dir):
    """Create a temporary memory file path."""
    return str(temp_dir / "test_memory.json")


@pytest.fixture
def temp_status_file(temp_dir):
    """Create a temporary status file path."""
    return str(temp_dir / "test_status.json")


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key")
    monkeypatch.setenv("GITHUB_TOKEN", "test_github_token")
