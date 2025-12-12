"""Tests for feedback loop improvements."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock

from nexusprime.agents.dev_squad import DevSquadAgent
from nexusprime.agents.council import CouncilAgent, ReviewerOpinion


class TestDevSquadFeedbackIntegration:
    """Test cases for Dev Squad feedback integration."""
    
    @patch('nexusprime.agents.dev_squad.get_llm_router')
    @patch('nexusprime.agents.dev_squad.save_status_snapshot')
    @patch('nexusprime.agents.dev_squad.validate_generated_code')
    @patch('nexusprime.agents.dev_squad.os.makedirs')
    @patch('nexusprime.agents.dev_squad.open', create=True)
    def test_initial_generation(self, mock_open, mock_makedirs, mock_validate, mock_save, mock_get_router):
        """Test Dev Squad initial code generation without feedback."""
        # Mock LLM router response
        mock_router = Mock()
        mock_router.call.return_value = ("print('Hello')", {"total_token_count": 50})
        mock_get_router.return_value = mock_router
        mock_validate.return_value = (True, [])
        
        agent = DevSquadAgent()
        state = {
            "spec_document": "Create a hello world program",
            "env_mode": "DEV",
            "total_tokens": {}
        }
        
        result = agent.execute(state)
        
        # Verify initial generation prompt was used
        call_args = mock_router.call.call_args
        prompt = call_args[1]['prompt']
        assert "Write the complete Python code" in prompt
        assert "FEEDBACKS DU COUNCIL" not in prompt
        
        # Verify code is saved to state
        assert "previous_code" in result
        assert result["previous_code"] == "print('Hello')"
    
    @patch('nexusprime.agents.dev_squad.get_llm_router')
    @patch('nexusprime.agents.dev_squad.save_status_snapshot')
    @patch('nexusprime.agents.dev_squad.validate_generated_code')
    @patch('nexusprime.agents.dev_squad.os.makedirs')
    @patch('nexusprime.agents.dev_squad.open', create=True)
    def test_revision_with_feedback(self, mock_open, mock_makedirs, mock_validate, mock_save, mock_get_router):
        """Test Dev Squad revision with Council feedback."""
        # Mock LLM router response
        mock_router = Mock()
        mock_router.call.return_value = ("print('Hello, World!')", {"total_token_count": 60})
        mock_get_router.return_value = mock_router
        mock_validate.return_value = (True, [])
        
        agent = DevSquadAgent()
        state = {
            "spec_document": "Create a hello world program",
            "env_mode": "DEV",
            "total_tokens": {},
            "previous_code": "print('Hello')",
            "review_comments": "Add punctuation and improve message"
        }
        
        result = agent.execute(state)
        
        # Verify revision prompt was used
        call_args = mock_router.call.call_args
        prompt = call_args[1]['prompt']
        assert "FEEDBACKS DU COUNCIL" in prompt
        assert "CODE ACTUEL" in prompt
        assert "print('Hello')" in prompt
        assert "Add punctuation" in prompt
        
        # Verify updated code is saved
        assert "previous_code" in result
        assert result["previous_code"] == "print('Hello, World!')"


class TestCouncilFeedbackFormatting:
    """Test cases for Council feedback formatting."""
    
    def test_format_concerns_for_dev_squad(self):
        """Test formatting of concerns for Dev Squad."""
        agent = CouncilAgent()
        
        opinions = [
            ReviewerOpinion(
                reviewer="Claude",
                model="claude-sonnet-4",
                score=75,
                reasoning="Good but needs improvements",
                concerns=["Missing error handling", "No tests"]
            ),
            ReviewerOpinion(
                reviewer="Gemini",
                model="gemini-2.5-pro",
                score=80,
                reasoning="Well structured",
                concerns=["Documentation incomplete"]
            ),
        ]
        
        feedback = agent._format_concerns_for_dev_squad(opinions)
        
        assert "CONCERNS À CORRIGER" in feedback
        assert "Claude" in feedback
        assert "Missing error handling" in feedback
        assert "No tests" in feedback
        assert "Gemini" in feedback
        assert "Documentation incomplete" in feedback
    
    def test_format_concerns_no_issues(self):
        """Test formatting when there are no concerns."""
        agent = CouncilAgent()
        
        opinions = [
            ReviewerOpinion(
                reviewer="Claude",
                model="claude-sonnet-4",
                score=95,
                reasoning="Excellent code",
                concerns=[]
            ),
        ]
        
        feedback = agent._format_concerns_for_dev_squad(opinions)
        
        assert "Aucun problème majeur" in feedback


class TestCouncilReportGeneration:
    """Test cases for Council report generation."""
    
    def test_report_with_improvements_section(self):
        """Test that report includes improvements section with history."""
        agent = CouncilAgent()
        
        opinions = [
            ReviewerOpinion(
                reviewer="Claude",
                model="claude-sonnet-4",
                score=85,
                reasoning="Much improved",
                concerns=[]
            ),
        ]
        
        previous_reviews = [
            {
                "reviewer": "Claude",
                "model": "claude-sonnet-4",
                "score": 75,
                "reasoning": "Needs work",
                "concerns": ["Missing tests"]
            }
        ]
        
        report = agent._generate_report(opinions, 85, "Good progress", previous_reviews)
        
        assert "AMÉLIORATIONS / CHANGEMENTS" in report
        assert "Claude: 75 → 85" in report
        assert "+10" in report
    
    def test_report_without_history(self):
        """Test that report works without previous reviews."""
        agent = CouncilAgent()
        
        opinions = [
            ReviewerOpinion(
                reviewer="Claude",
                model="claude-sonnet-4",
                score=85,
                reasoning="Good work",
                concerns=[]
            ),
        ]
        
        report = agent._generate_report(opinions, 85, "Well done", None)
        
        assert "COUNCIL MULTI-LLM REVIEW REPORT" in report
        assert "Claude" in report
        # Should not have improvements section
        assert "AMÉLIORATIONS / CHANGEMENTS" not in report


class TestStateFields:
    """Test cases for new state fields."""
    
    def test_state_has_required_fields(self):
        """Test that NexusFactoryState has the new required fields."""
        from nexusprime.core.state import NexusFactoryState
        
        # Verify the TypedDict has the expected annotations
        annotations = NexusFactoryState.__annotations__
        
        assert "previous_code" in annotations
        assert "previous_reviews" in annotations
        assert "review_comments" in annotations
        assert annotations["previous_code"] == str
        assert annotations["review_comments"] == str
