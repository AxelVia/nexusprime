"""Tests for agent modules."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch

from nexusprime.agents import ProductOwnerAgent
from langchain_core.messages import HumanMessage


class TestProductOwnerAgent:
    """Test cases for ProductOwnerAgent."""
    
    @patch('nexusprime.agents.product_owner.get_llm_router')
    @patch('nexusprime.agents.product_owner.save_status_snapshot')
    def test_execute(self, mock_save, mock_get_router):
        """Test ProductOwnerAgent execution."""
        # Mock LLM router response
        mock_router = Mock()
        mock_router.call.return_value = ("# SPEC\nTest spec", {"total_token_count": 100})
        mock_get_router.return_value = mock_router
        
        agent = ProductOwnerAgent()
        state = {
            "messages": [HumanMessage(content="Create a calculator")],
            "total_tokens": {}
        }
        
        result = agent.execute(state)
        
        assert "spec_document" in result
        assert result["spec_document"] == "# SPEC\nTest spec"
        assert "current_status" in result
        assert "Product Owner" in result["current_status"]
        
        # Verify LLM router was called with correct agent name
        mock_router.call.assert_called_once()
        call_args = mock_router.call.call_args
        assert call_args[1]['agent_name'] == 'product_owner'
