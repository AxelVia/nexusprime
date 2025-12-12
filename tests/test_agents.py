"""Tests for agent modules."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch

from nexusprime.agents import ProductOwnerAgent
from langchain_core.messages import HumanMessage


class TestProductOwnerAgent:
    """Test cases for ProductOwnerAgent."""
    
    @patch('nexusprime.agents.product_owner.call_llm')
    @patch('nexusprime.agents.product_owner.save_status_snapshot')
    def test_execute(self, mock_save, mock_call_llm):
        """Test ProductOwnerAgent execution."""
        # Mock LLM response
        mock_call_llm.return_value = ("# SPEC\nTest spec", {"total_token_count": 100})
        
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
        
        # Verify LLM was called
        mock_call_llm.assert_called_once()
