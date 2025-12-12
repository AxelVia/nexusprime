"""Tests for refactored Multi-API LLM router module."""

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
        assert LLMProvider.CLAUDE_SONNET_4.value == "claude-sonnet-4-20250514"
        assert LLMProvider.GEMINI_3_PRO.value == "gemini-3-pro"
        assert LLMProvider.GROK_3.value == "azureml-xai/grok-3"
        assert LLMProvider.GPT_5.value == "azure-openai/gpt-5"
    
    def test_provider_is_string_enum(self):
        """Test that LLMProvider is a string enum for compatibility."""
        assert isinstance(LLMProvider.CLAUDE_SONNET_4, str)
        assert isinstance(LLMProvider.GEMINI_3_PRO, str)
        # Test string comparison works
        assert LLMProvider.CLAUDE_SONNET_4 == "claude-sonnet-4-20250514"


class TestLLMConfig:
    """Test cases for LLMConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = LLMConfig(provider=LLMProvider.CLAUDE_SONNET_4)
        assert config.provider == LLMProvider.CLAUDE_SONNET_4
        assert config.temperature == 0.2
        assert config.max_tokens == 8192
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = LLMConfig(
            provider=LLMProvider.GPT_5,
            temperature=0.7,
            max_tokens=2000
        )
        assert config.provider == LLMProvider.GPT_5
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
        assert po_config.provider == LLMProvider.CLAUDE_SONNET_4
        assert po_config.temperature == 0.3
        
        # Check tech_lead mapping
        tl_config = router.AGENT_MODEL_MAP["tech_lead"]
        assert tl_config.provider == LLMProvider.GEMINI_3_PRO
        assert tl_config.temperature == 0.2
        
        # Check dev_squad mapping
        ds_config = router.AGENT_MODEL_MAP["dev_squad"]
        assert ds_config.provider == LLMProvider.CLAUDE_SONNET_4
        assert ds_config.temperature == 0.1
        
        # Check council mappings
        council_gpt = router.AGENT_MODEL_MAP["council_gpt"]
        assert council_gpt.provider == LLMProvider.GPT_5
        assert council_gpt.temperature == 0.4
        
        council_grok = router.AGENT_MODEL_MAP["council_grok"]
        assert council_grok.provider == LLMProvider.GROK_3
        assert council_grok.temperature == 0.4
        
        council_gemini = router.AGENT_MODEL_MAP["council_gemini"]
        assert council_gemini.provider == LLMProvider.GEMINI_3_PRO
        assert council_gemini.temperature == 0.4
        
        council_claude = router.AGENT_MODEL_MAP["council_claude"]
        assert council_claude.provider == LLMProvider.CLAUDE_SONNET_4
        assert council_claude.temperature == 0.4
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    @patch('nexusprime.core.llm_router.httpx.Client')
    def test_call_anthropic(self, mock_client_class, mock_env):
        """Test successful Anthropic API call."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {
                    "text": "Test response from Claude"
                }
            ],
            "usage": {
                "input_tokens": 15,
                "output_tokens": 25
            }
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_class.return_value = mock_client_instance
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_anthropic_key'}):
            router = GitHubModelsRouter()
            content, usage = router.call(
                prompt="Test prompt",
                agent_name="product_owner"
            )
        
        assert content == "Test response from Claude"
        assert usage["prompt_tokens"] == 15
        assert usage["completion_tokens"] == 25
        assert usage["total_token_count"] == 40
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    @patch('nexusprime.core.llm_router.httpx.Client')
    def test_call_github_models(self, mock_client_class, mock_env):
        """Test successful GitHub Models API call."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response from Grok"
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
            agent_name="council_grok"
        )
        
        assert content == "Test response from Grok"
        assert usage["prompt_tokens"] == 10
        assert usage["completion_tokens"] == 20
        assert usage["total_token_count"] == 30
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    def test_call_google_without_api_key(self, mock_env):
        """Test that Google API call fails without API key."""
        router = GitHubModelsRouter()
        
        with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
            router.call(
                prompt="Test prompt",
                agent_name="tech_lead"
            )
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    def test_call_anthropic_without_api_key(self, mock_env):
        """Test that Anthropic API call fails without API key."""
        router = GitHubModelsRouter()
        
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            router.call(
                prompt="Test prompt",
                agent_name="product_owner"
            )
    
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
            provider=LLMProvider.GPT_5,
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
        assert payload['model'] == "azure-openai/gpt-5"
        assert payload['temperature'] == 0.8
        assert payload['max_tokens'] == 1000
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    def test_list_available_models(self, mock_env):
        """Test listing available models."""
        router = GitHubModelsRouter()
        models = router.list_available_models()
        
        assert "claude-sonnet-4-20250514" in models
        assert "gemini-3-pro" in models
        assert "azureml-xai/grok-3" in models
        assert "azure-openai/gpt-5" in models
    
    @patch('nexusprime.core.llm_router.get_required_env', return_value='test_token')
    def test_get_model_for_agent(self, mock_env):
        """Test getting model for specific agent."""
        router = GitHubModelsRouter()
        
        assert router.get_model_for_agent("product_owner") == "claude-sonnet-4-20250514"
        assert router.get_model_for_agent("tech_lead") == "gemini-3-pro"
        assert router.get_model_for_agent("council_gpt") == "azure-openai/gpt-5"
        assert router.get_model_for_agent("council_grok") == "azureml-xai/grok-3"
        assert router.get_model_for_agent("unknown") == "claude-sonnet-4-20250514"


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
