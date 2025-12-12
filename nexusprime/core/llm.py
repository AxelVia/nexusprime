"""LLM configuration and helper functions."""

from __future__ import annotations

from typing import Dict, Tuple

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..config import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


_llm_instance: ChatGoogleGenerativeAI | None = None


def get_llm() -> ChatGoogleGenerativeAI:
    """
    Get or create the LLM instance.
    
    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    global _llm_instance
    if _llm_instance is None:
        settings = get_settings()
        _llm_instance = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            convert_system_message_to_human=True
        )
        logger.info(f"LLM initialized: {settings.llm_model} (temp={settings.llm_temperature})")
    return _llm_instance


def call_llm(prompt: str, system_prompt: str = "You are a precise coding agent.") -> Tuple[str, Dict[str, int]]:
    """
    Call the LLM with given prompts.
    
    Args:
        prompt: User prompt
        system_prompt: System prompt (default: "You are a precise coding agent.")
    
    Returns:
        Tuple of (response_content, token_usage)
    
    Raises:
        Exception: If LLM call fails
    """
    try:
        llm = get_llm()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        
        # Extract usage metadata
        usage = response.response_metadata.get("token_usage", {})
        
        logger.debug(f"LLM call successful. Tokens: {usage.get('total_token_count', 0)}")
        return response.content, usage
        
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise
