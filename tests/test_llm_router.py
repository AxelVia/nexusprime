"""Tests for LLM router module."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock

from nexusprime.core.llm_router import (
    LLMProvider,
    LLMConfig,
    CopilotLLMRouter,
    get_llm_router
)


class TestLLMProvider:
    """Test cases for LLMProvider enum."""
    
    def test_provider_values(self):
        """Test that all provider values are correct."""
        assert LLMProvider.CLAUDE.value == "claude-sonnet-4"
        assert LLMProvider.GEMINI.value == "gemini-2.5-pro"
        assert LLMProvider.GPT4.value == "gpt-4o"
        assert LLMProvider.GROK.value == "grok-3"
    
    def test_provider_is_string_enum(self):
        """Test that LLMProvider is a string enum."""
        assert isinstance(LLMProvider.CLAUDE, str)
        assert isinstance(LLMProvider.GEMINI, str)


class TestLLMConfig:
    """Test cases for LLMConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = LLMConfig(provider=LLMProvider.CLAUDE)
        assert config.provider == LLMProvider.CLAUDE
        assert config.temperature == 0.2
        assert config.max_tokens == 4000
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = LLMConfig(
            provider=LLMProvider.GROK,
            temperature=0.7,
            max_tokens=2000
        )
        assert config.provider == LLMProvider.GROK
        assert config.temperature == 0.7
        assert config.max_tokens == 2000


class TestCopilotLLMRouter:
    """Test cases for CopilotLLMRouter."""
    
    def test_agent_model_mapping(self):
        """Test that agent model mapping is correct."""
        router = CopilotLLMRouter()
        
        # Check product_owner mapping
        po_config = router.AGENT_MODEL_MAPPING["product_owner"]
        assert po_config.provider == LLMProvider.CLAUDE
        assert po_config.temperature == 0.3
        
        # Check tech_lead mapping
        tl_config = router.AGENT_MODEL_MAPPING["tech_lead"]
        assert tl_config.provider == LLMProvider.GEMINI
        assert tl_config.temperature == 0.2
        
        # Check dev_squad mapping
        ds_config = router.AGENT_MODEL_MAPPING["dev_squad"]
        assert ds_config.provider == LLMProvider.CLAUDE
        assert ds_config.temperature == 0.1
        
        # Check council mappings
        council_grok = router.AGENT_MODEL_MAPPING["council_grok"]
        assert council_grok.provider == LLMProvider.GROK
        assert council_grok.temperature == 0.4
        
        council_gemini = router.AGENT_MODEL_MAPPING["council_gemini"]
        assert council_gemini.provider == LLMProvider.GEMINI
        assert council_gemini.temperature == 0.4
        
        council_claude = router.AGENT_MODEL_MAPPING["council_claude"]
        assert council_claude.provider == LLMProvider.CLAUDE
        assert council_claude.temperature == 0.3
    
    @patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'})
    @patch('nexusprime.core.llm_router.httpx.Client')
    def test_call_success(self, mock_client_class):
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
        
        mock_client = MagicMock()
        mock_client.__enter__.return_value.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        router = CopilotLLMRouter()
        content, usage = router.call(
            prompt="Test prompt",
            agent_name="product_owner"
        )
        
        assert content == "Test response"
        assert usage["prompt_tokens"] == 10
        assert usage["completion_tokens"] == 20
        assert usage["total_token_count"] == 30
    
    @patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'})
    @patch('nexusprime.core.llm_router.httpx.Client')
    def test_call_with_custom_config(self, mock_client_class):
        """Test LLM call with custom configuration."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Custom response"}}],
            "usage": {"total_tokens": 50}
        }
        
        mock_client = MagicMock()
        mock_client.__enter__.return_value.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        router = CopilotLLMRouter()
        custom_config = LLMConfig(
            provider=LLMProvider.GPT4,
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
        call_args = mock_client.__enter__.return_value.post.call_args
        payload = call_args[1]['json']
        assert payload['model'] == "gpt-4o"
        assert payload['temperature'] == 0.8
        assert payload['max_tokens'] == 1000
    
    @patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'})
    @patch('nexusprime.core.llm_router.httpx.Client')
    def test_call_with_unknown_agent(self, mock_client_class):
        """Test that unknown agent gets default config."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Default response"}}],
            "usage": {}
        }
        
        mock_client = MagicMock()
        mock_client.__enter__.return_value.post.return_value = mock_response
        mock_client_class.return_value = mock_client
        
        router = CopilotLLMRouter()
        content, _ = router.call(
            prompt="Test",
            agent_name="nonexistent_agent"
        )
        
        # Verify default config was used
        call_args = mock_client.__enter__.return_value.post.call_args
        payload = call_args[1]['json']
        assert payload['model'] == "claude-sonnet-4"
        assert payload['temperature'] == 0.2


class TestGetLLMRouter:
    """Test cases for get_llm_router singleton."""
    
    def test_singleton_behavior(self):
        """Test that get_llm_router returns the same instance."""
        router1 = get_llm_router()
        router2 = get_llm_router()
        
        assert router1 is router2
        assert isinstance(router1, CopilotLLMRouter)
    
    def test_singleton_is_copilot_router(self):
        """Test that singleton is a CopilotLLMRouter instance."""
        router = get_llm_router()
        assert isinstance(router, CopilotLLMRouter)
        assert hasattr(router, 'AGENT_MODEL_MAPPING')
        assert hasattr(router, 'call')
