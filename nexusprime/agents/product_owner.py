"""Product Owner agent."""

from __future__ import annotations

from typing import Any, Dict

from .base import Agent
from ..core.llm_router import get_llm_router
from ..core.state import NexusFactoryState
from ..utils.tokens import update_token_usage
from ..utils.status import save_status_snapshot


class ProductOwnerAgent(Agent):
    """Product Owner: Refines requirements into a SPEC.md."""
    
    def execute(self, state: NexusFactoryState) -> Dict[str, Any]:
        """
        Refine user requirements into a specification document.
        
        Args:
            state: Current factory state
        
        Returns:
            State updates with spec_document and token usage
        """
        self.log_execution("Refining specification")
        
        # Get latest user message
        messages = state.get("messages", [])
        if messages:
            last_msg = messages[-1].content
        else:
            last_msg = "No input provided."
            self.logger.warning("No input message found")
        
        # Generate specification
        prompt = f"Generate a strict SPEC.md for this request: {last_msg}"
        try:
            router = get_llm_router()
            spec, usage = router.call(
                prompt=prompt,
                agent_name="product_owner"
            )
            new_tokens = update_token_usage(state.get("total_tokens", {}), usage)
            
            state_update = {
                "current_status": "Agent: Product Owner (Refining Spec)",
                "spec_document": spec,
                "total_tokens": new_tokens
            }
            
            save_status_snapshot({**state, **state_update})
            self.log_execution("Specification created successfully")
            
            return state_update
            
        except Exception as e:
            self.logger.error(f"Failed to generate specification: {e}")
            raise
