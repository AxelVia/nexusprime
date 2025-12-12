"""Council agent."""

from __future__ import annotations

import os
from typing import Any, Dict

from .base import Agent
from ..core.llm import call_llm
from ..core.state import NexusFactoryState
from ..integrations.memory import NexusMemory
from ..integrations.github_client import GitHubClient
from ..utils.tokens import update_token_usage
from ..utils.status import save_status_snapshot
from ..config import get_settings


class CouncilAgent(Agent):
    """The Council: Validates quality and decides next step."""
    
    def __init__(self):
        """Initialize Council agent."""
        super().__init__()
        settings = get_settings()
        self.memory = NexusMemory(memory_path=settings.memory_file)
        self.github_client: GitHubClient | None = None
        self.settings = settings
    
    def _get_github_client(self) -> GitHubClient:
        """Get or create GitHub client."""
        if self.github_client is None:
            self.github_client = GitHubClient()
        return self.github_client
    
    def execute(self, state: NexusFactoryState) -> Dict[str, Any]:
        """
        Review code quality and archive lessons if approved.
        
        Args:
            state: Current factory state
        
        Returns:
            State updates with quality score and feedback
        """
        self.log_execution("Reviewing code quality")
        
        env = state.get("env_mode", "DEV")
        spec = state.get("spec_document", "")
        
        # Review specification quality
        prompt = f"""
You are The Council, a strict AI auditor.
Review the following Specification and grant a Quality Score (0-100).

SPEC:
{spec[:1000]}...

CRITERIA:
- Clarity
- Security
- Robustness

Return ONLY an integer.
"""
        
        try:
            score_str, usage = call_llm(
                prompt,
                system_prompt="You are a strict code auditor. Output only the integer score."
            )
            # Extract numeric score
            new_score = int(''.join(filter(str.isdigit, score_str)))
            new_tokens = update_token_usage(state.get("total_tokens", {}), usage)
        except (ValueError, AttributeError) as e:
            self.logger.error(f"Failed to parse quality score: {e}. Using default.")
            new_score = 70
            new_tokens = state.get("total_tokens", {})
        except Exception as e:
            self.logger.error(f"Failed to get quality score: {e}")
            new_score = 70
            new_tokens = state.get("total_tokens", {})
        
        self.logger.info(f"Quality score: {new_score}/100")
        
        # Check for approval
        is_approved = (
            (env == "DEV" and new_score > self.settings.dev_quality_threshold) or
            (env == "PROD" and new_score > self.settings.prod_quality_threshold)
        )
        
        if is_approved:
            self.log_execution("APPROVAL GRANTED - Archiving lesson")
            
            # Store lesson in memory
            try:
                self.memory.store_lesson(
                    topic="Feature Implementation",
                    context=spec[:50] + "...",
                    outcome="Success",
                    solution=f"Followed Spec, achieved quality score of {new_score}"
                )
            except Exception as e:
                self.logger.error(f"Failed to store lesson: {e}")
            
            # Push to GitHub
            self._push_to_github(env)
        else:
            self.log_execution(f"Quality threshold not met ({new_score}). Requesting revision.")
        
        state_update = {
            "current_status": "Agent: The Council (Reviewing)",
            "quality_score": new_score,
            "feedback_loop_count": state.get("feedback_loop_count", 0) + 1,
            "total_tokens": new_tokens
        }
        
        save_status_snapshot({**state, **state_update})
        
        return state_update
    
    def _push_to_github(self, env: str) -> None:
        """
        Push generated files to GitHub.
        
        Args:
            env: Current environment mode
        """
        try:
            github_client = self._get_github_client()
            repo = github_client.get_or_create_repo("nexus-prime-workspace")
            
            # Push workspace files
            workspace_dir = self.settings.workspace_dir
            files = ["app_dev.py", "app_prod.py"]
            
            for fname in files:
                fpath = os.path.join(workspace_dir, fname)
                if os.path.exists(fpath):
                    github_client.push_local_file(
                        repo,
                        fpath,
                        fname,
                        f"Update {fname} by NexusPrime"
                    )
            
            self.log_execution("Files pushed to GitHub successfully")
            
        except Exception as e:
            self.logger.error(f"GitHub push failed: {e}")
