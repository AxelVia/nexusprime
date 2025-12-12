"""Multi-LLM Router for NexusPrime using GitHub Copilot API."""

from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple

import httpx

from ..utils.logging import get_logger

logger = get_logger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers via GitHub Copilot API."""
    
    CLAUDE = "claude-sonnet-4"
    GEMINI = "gemini-2.5-pro"
    GPT4 = "gpt-4o"
    GROK = "grok-3"


@dataclass
class LLMConfig:
    """Configuration for LLM calls."""
    
    provider: LLMProvider
    temperature: float = 0.2
    max_tokens: int = 4000


class CopilotLLMRouter:
    """Router for multi-LLM calls via GitHub Copilot API."""
    
    # Agent to model mapping with specific configurations
    AGENT_MODEL_MAPPING: Dict[str, LLMConfig] = {
        "product_owner": LLMConfig(provider=LLMProvider.CLAUDE, temperature=0.3),
        "tech_lead": LLMConfig(provider=LLMProvider.GEMINI, temperature=0.2),
        "dev_squad": LLMConfig(provider=LLMProvider.CLAUDE, temperature=0.1),
        "council_grok": LLMConfig(provider=LLMProvider.GROK, temperature=0.4),
        "council_gemini": LLMConfig(provider=LLMProvider.GEMINI, temperature=0.4),
        "council_claude": LLMConfig(provider=LLMProvider.CLAUDE, temperature=0.3),
    }
    
    def __init__(self):
        """Initialize the LLM router."""
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            logger.warning("GITHUB_TOKEN not found. LLM router may not work.")
        
        self.api_url = "https://api.githubcopilot.com/chat/completions"
        logger.info("CopilotLLMRouter initialized")
    
    def call(
        self,
        prompt: str,
        agent_name: str,
        system_prompt: str = "You are a precise coding agent.",
        custom_config: LLMConfig | None = None
    ) -> Tuple[str, Dict[str, int]]:
        """
        Call the appropriate LLM based on agent name.
        
        Args:
            prompt: User prompt
            agent_name: Name of the agent making the call
            system_prompt: System prompt (default: "You are a precise coding agent.")
            custom_config: Optional custom LLM configuration
        
        Returns:
            Tuple of (response_content, token_usage)
        
        Raises:
            Exception: If LLM call fails
        """
        # Get configuration for this agent
        config = custom_config or self.AGENT_MODEL_MAPPING.get(
            agent_name,
            LLMConfig(provider=LLMProvider.CLAUDE, temperature=0.2)
        )
        
        logger.debug(
            f"Calling {config.provider.value} for agent '{agent_name}' "
            f"(temp={config.temperature})"
        )
        
        try:
            # Prepare request payload
            payload = {
                "model": config.provider.value,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": config.temperature,
                "max_tokens": config.max_tokens
            }
            
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Content-Type": "application/json"
            }
            
            # Make API call
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
            
            # Extract response content
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Extract token usage
            usage = data.get("usage", {})
            token_usage = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_token_count": usage.get("total_tokens", 0)
            }
            
            logger.debug(
                f"LLM call successful. Tokens: {token_usage.get('total_token_count', 0)}"
            )
            
            return content, token_usage
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {config.provider.value}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to call {config.provider.value}: {e}")
            raise


# Singleton instance
_router_instance: CopilotLLMRouter | None = None
_router_lock = threading.Lock()


def get_llm_router() -> CopilotLLMRouter:
    """
    Get or create the LLM router instance (thread-safe singleton).
    
    Returns:
        CopilotLLMRouter instance
    """
    global _router_instance
    if _router_instance is None:
        with _router_lock:
            # Double-check locking pattern
            if _router_instance is None:
                _router_instance = CopilotLLMRouter()
                logger.info("LLM router singleton created")
    return _router_instance
