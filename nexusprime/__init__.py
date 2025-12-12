"""
NexusPrime - AI Software Factory
================================

A multi-agent system for automated software development using LangGraph.
"""

from __future__ import annotations

__version__ = "1.0.0"

from .core import build_nexus_factory, NexusFactoryState
from .config import get_settings
from .integrations import NexusMemory, GitHubClient

__all__ = [
    'build_nexus_factory',
    'NexusFactoryState',
    'get_settings',
    'NexusMemory',
    'GitHubClient',
]
