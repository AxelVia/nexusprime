"""Tests for LLM router module."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock

from nexusprime.core.llm_router import (
    LLMProvider,
    LLMConfig,
    GitHubModelsRouter,
    CopilotLLMRouter,
    get_llm_router
)


class TestLLMProvider:
    """Test cases for LLMProvider enum."""
    
    def test_provider_values(self):
        """Test that all provider values are correct."""
        assert LLMProvider.CLAUDE_SONNET.value == "anthropic/claude-sonnet-4"
        assert LLMProvider.GEMINI_PRO.value == "google/gemini-2.5-pro"
        assert LLMProvider.GPT4O.value == "openai/gpt-4o"
        assert LLMProvider.GPT4O_MINI.value == "openai/gpt-4o-mini"
    
    def test_provider_is_string_enum(self):
        """Test that LLMProvider is a string enum for compatibility."""
        assert isinstance(LLMProvider.CLAUDE_SONNET, str)
        assert isinstance(LLMProvider.GEMINI_PRO, str)
        # Test string comparison works
        assert LLMProvider.CLAUDE_SONNET == "anthropic/claude-sonnet-4"


class TestLLMConfig:
    """Test cases for LLMConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = LLMConfig(provider=LLMProvider.CLAUDE_SONNET)
        assert config.provider == LLMProvider.CLAUDE_SONNET
        assert config.temperature == 0.2
        assert config.max_tokens == 8192
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = LLMConfig(
            provider=LLMProvider.GPT4O,
            temperature=0.7,
            max_tokens=2000
        )
        assert config.provider == LLMProvider.GPT4O
        assert config.temperature == 0.7
        assert config.max_tokens == 2000


class TestGitHubModelsRouter:
    """Test cases for GitHubModelsRouter."""
    
    def test_agent_model_mapping(self):
        """Test that agent model mapping is correct."""
        # Test with a mock token to avoid environment dependency
        with patch('nexusprime.core.llm_router.get_required_env', return_value='mock_token'):
            router = GitHubModelsRouter()
        
        # Check product_owner mapping
        po_config = router.AGENT_MODEL_MAP["product_owner"]
        assert po_config.provider == LLMProvider.CLAUDE_SONNET
        assert po_config.temperature == 0.3
        
        # Check tech_lead mapping
        tl_config = router.AGENT_MODEL_MAP["tech_lead"]
        assert tl_config.provider == LLMProvider.GEMINI_PRO
        assert tl_config.temperature == 0.2
        
        # Check dev_squad mapping
        ds_config = router.AGENT_MODEL_MAP["dev_squad"]
        assert ds_config.provider == LLMProvider.CLAUDE_SONNET
        assert ds_config.temperature == 0.1
        
        # Check council mappings
        council_gpt4 = router.AGENT_MODEL_MAP["council_gpt4"]
        assert council_gpt4.provider == LLMProvider.GPT4O
        assert council_gpt4.temperature == 0.4
        
        council_gemini = router.AGENT_MODEL_MAP["council_gemini"]
        assert council_gemini.provider == LLMProvider.GEMINI_PRO
        assert council_gemini.temperature == 0.4
        
        council_claude = router.AGENT_MODEL_MAP["council_claude"]
        assert council_claude.provider == LLMProvider.CLAUDE_SONNET
        assert council_claude.temperature == 0.4
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    @patch('nexusprime.core.llm_router.httpx.Client')
    def test_call_success(self, mock_client_class, mock_env):
        """Test successful LLM call."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        
        router = GitHubModelsRouter()
        content, usage = router.call(
            prompt="Test prompt",
            agent_name="product_owner"
        )
        
        assert content == "Test response"
        assert usage["prompt_tokens"] == 10
        assert usage["completion_tokens"] == 20
        assert usage["total_token_count"] == 30
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    @patch('nexusprime.core.llm_router.httpx.Client')
    def test_call_with_custom_config(self, mock_client_class, mock_env):
        """Test LLM call with custom configuration."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Custom response"}}],
            "usage": {"total_tokens": 50}
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        
        router = GitHubModelsRouter()
        custom_config = LLMConfig(
            provider=LLMProvider.GPT4O,
            temperature=0.8,
            max_tokens=1000
        )
        
        content, usage = router.call(
            prompt="Custom test",
            agent_name="unknown_agent",
            custom_config=custom_config
        )
        
        assert content == "Custom response"
        
        # Verify the request was made with custom config
        call_args = mock_client_instance.post.call_args
        payload = call_args[1]['json']
        assert payload['model'] == "openai/gpt-4o"
        assert payload['temperature'] == 0.8
        assert payload['max_tokens'] == 1000
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    @patch('nexusprime.core.llm_router.httpx.Client')
    def test_call_with_unknown_agent(self, mock_client_class, mock_env):
        """Test that unknown agent gets default config."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Default response"}}],
            "usage": {}
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        
        router = GitHubModelsRouter()
        content, _ = router.call(
            prompt="Test",
            agent_name="nonexistent_agent"
        )
        
        # Verify default config was used
        call_args = mock_client_instance.post.call_args
        payload = call_args[1]['json']
        assert payload['model'] == "anthropic/claude-sonnet-4"
        assert payload['temperature'] == 0.2
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    def test_list_available_models(self, mock_env):
        """Test listing available models."""
        router = GitHubModelsRouter()
        models = router.list_available_models()
        
        assert "anthropic/claude-sonnet-4" in models
        assert "google/gemini-2.5-pro" in models
        assert "openai/gpt-4o" in models
        assert "openai/gpt-4o-mini" in models
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    def test_get_model_for_agent(self, mock_env):
        """Test getting model for specific agent."""
        router = GitHubModelsRouter()
        
        assert router.get_model_for_agent("product_owner") == "anthropic/claude-sonnet-4"
        assert router.get_model_for_agent("tech_lead") == "google/gemini-2.5-pro"
        assert router.get_model_for_agent("council_gpt4") == "openai/gpt-4o"
        assert router.get_model_for_agent("unknown") == "anthropic/claude-sonnet-4"


class TestCopilotLLMRouterAlias:
    """Test that CopilotLLMRouter is an alias for GitHubModelsRouter."""
    
    def test_alias(self):
        """Test that CopilotLLMRouter is the same as GitHubModelsRouter."""
        assert CopilotLLMRouter is GitHubModelsRouter


class TestGetLLMRouter:
    """Test cases for get_llm_router singleton."""
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    def test_singleton_behavior(self, mock_env):
        """Test that get_llm_router returns the same instance."""
        # Clear singleton for test
        import nexusprime.core.llm_router as router_module
        router_module._router_instance = None
        
        router1 = get_llm_router()
        router2 = get_llm_router()
        
        assert router1 is router2
        assert isinstance(router1, GitHubModelsRouter)
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    def test_singleton_is_github_models_router(self, mock_env):
        """Test that singleton is a GitHubModelsRouter instance."""
        # Clear singleton for test
        import nexusprime.core.llm_router as router_module
        router_module._router_instance = None
        
        router = get_llm_router()
        assert isinstance(router, GitHubModelsRouter)
        assert hasattr(router, 'AGENT_MODEL_MAP')
        assert hasattr(router, 'call')
        assert hasattr(router, 'list_available_models')
        assert hasattr(router, 'get_model_for_agent')
