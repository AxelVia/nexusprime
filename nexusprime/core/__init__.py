"""Core modules for NexusPrime."""

from .state import NexusFactoryState
from .llm import call_llm, get_llm
from .graph import build_nexus_factory
from .llm_router import (
    GitHubModelsRouter,
    CopilotLLMRouter,  # Alias
    get_llm_router,
    LLMProvider,
    LLMConfig
)

__all__ = [
    'NexusFactoryState',
    'call_llm',
    'get_llm',
    'build_nexus_factory',
    'GitHubModelsRouter',
    'CopilotLLMRouter',
    'get_llm_router',
    'LLMProvider',
    'LLMConfig'
]
