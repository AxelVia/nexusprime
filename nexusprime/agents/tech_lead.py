"""Tech Lead agent."""

from __future__ import annotations

from typing import Any, Dict

from .base import Agent
from ..core.llm import call_llm
from ..core.state import NexusFactoryState
from ..integrations.memory import NexusMemory
from ..integrations.github_client import GitHubClient
from ..utils.tokens import update_token_usage
from ..utils.status import save_status_snapshot
from ..config import get_settings


class TechLeadAgent(Agent):
    """Tech Lead: Sets up environment and dispatches to Dev Squad."""
    
    def __init__(self):
        """Initialize Tech Lead agent."""
        super().__init__()
        settings = get_settings()
        self.memory = NexusMemory(memory_path=settings.memory_file)
        self.github_client: GitHubClient | None = None
    
    def _get_github_client(self) -> GitHubClient:
        """Get or create GitHub client."""
        if self.github_client is None:
            self.github_client = GitHubClient()
        return self.github_client
    
    def execute(self, state: NexusFactoryState) -> Dict[str, Any]:
        """
        Set up environment and retrieve context from memory.
        
        Args:
            state: Current factory state
        
        Returns:
            State updates with environment mode and memory context
        """
        self.log_execution("Setting up environment")
        
        spec = state.get("spec_document", "")
        
        # 1. Retrieve lessons from memory
        memory_ctx = self.memory.retrieve_context(spec)
        self.logger.info(f"Retrieved context: {len(memory_ctx)} characters")
        
        # 2. Determine environment (AI decision)
        env_prompt = (
            f"Based on this compiled spec, does the user want a Production-ready system "
            f"or a Prototype? Return ONLY 'PROD' or 'DEV'.\n\nSPEC EXCERPT:\n{spec[:500]}"
        )
        
        try:
            env_decision, usage = call_llm(
                env_prompt,
                system_prompt="You are a Tech Lead. Output only PROD or DEV."
            )
            env_mode = "PROD" if "PROD" in env_decision.upper() else "DEV"
            new_tokens = update_token_usage(state.get("total_tokens", {}), usage)
        except Exception as e:
            self.logger.error(f"Failed to determine environment, defaulting to DEV: {e}")
            env_mode = "DEV"
            new_tokens = state.get("total_tokens", {})
        
        self.logger.info(f"Environment set to: {env_mode}")
        
        # 3. GitHub integration
        repo_url = "N/A"
        try:
            github_client = self._get_github_client()
            repo = github_client.get_or_create_repo(
                "nexus-prime-workspace",
                description="Automated Factory Workspace",
                private=True
            )
            repo_url = repo.html_url
        except Exception as e:
            self.logger.error(f"GitHub setup error (non-blocking): {e}")
        
        state_update = {
            "current_status": "Agent: Tech Lead (Setup & Dispatch)",
            "env_mode": env_mode,
            "memory_context": memory_ctx,
            "repo_url": repo_url,
            "total_tokens": new_tokens
        }
        
        save_status_snapshot({**state, **state_update})
        self.log_execution("Environment setup complete")
        
        return state_update
