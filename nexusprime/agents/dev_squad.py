"""Dev Squad agent."""

from __future__ import annotations

import os
from typing import Any, Dict

from .base import Agent
from ..core.llm_router import get_llm_router
from ..core.state import NexusFactoryState
from ..utils.tokens import update_token_usage
from ..utils.status import save_status_snapshot
from ..utils.security import validate_generated_code
from ..config import get_settings


class DevSquadAgent(Agent):
    """Dev Squad: Writes code and runs tests."""
    
    def execute(self, state: NexusFactoryState) -> Dict[str, Any]:
        """
        Generate code based on specification.
        
        Args:
            state: Current factory state
        
        Returns:
            State updates with file system state and token usage
        """
        self.log_execution("Starting code generation")
        
        settings = get_settings()
        spec = state.get("spec_document", "")
        env = state.get("env_mode", "DEV")
        
        # Generate code using LLM
        prompt = (
            f"Write the complete Python code for the following specification. "
            f"Return ONLY the code, no markdown.\n\nSPEC:\n{spec}"
        )
        
        try:
            router = get_llm_router()
            code_content, usage = router.call(
                prompt=prompt,
                agent_name="dev_squad",
                system_prompt="You are a senior Python developer. Write clean, production-ready code."
            )
            
            # Strip markdown code fences if present
            code_content = code_content.replace("```python", "").replace("```", "").strip()
            
            # Validate generated code for security
            is_safe, warnings = validate_generated_code(code_content)
            if not is_safe:
                for warning in warnings:
                    self.logger.warning(f"Security concern: {warning}")
            
            # Write code to filesystem
            workspace_dir = settings.workspace_dir
            if not os.path.exists(workspace_dir):
                os.makedirs(workspace_dir)
                self.logger.info(f"Created workspace directory: {workspace_dir}")
            
            file_path = os.path.join(workspace_dir, f"app_{env.lower()}.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_content)
            
            self.logger.info(f"Code written to {file_path}")
            
            new_tokens = update_token_usage(state.get("total_tokens", {}), usage)
            
            state_update = {
                "current_status": "Agent: Dev Squad (Coding)",
                "file_system_state": {file_path: "generated_by_gemini"},
                "total_tokens": new_tokens
            }
            
            save_status_snapshot({**state, **state_update})
            self.log_execution("Code generation complete")
            
            return state_update
            
        except Exception as e:
            self.logger.error(f"Failed to generate code: {e}")
            raise
