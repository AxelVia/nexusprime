"""Token usage management utilities."""

from __future__ import annotations

from typing import Dict


def update_token_usage(current_usage: Dict[str, int], new_usage: Dict[str, int]) -> Dict[str, int]:
    """
    Merge token usage from a new LLM call into cumulative usage.
    
    Args:
        current_usage: Current cumulative token usage
        new_usage: Token usage from latest LLM call (Gemini format)
    
    Returns:
        Updated token usage dictionary
    """
    return {
        "prompt_tokens": current_usage.get("prompt_tokens", 0) + new_usage.get("prompt_token_count", 0),
        "completion_tokens": current_usage.get("completion_tokens", 0) + new_usage.get("candidates_token_count", 0),
        "total_tokens": current_usage.get("total_tokens", 0) + new_usage.get("total_token_count", 0)
    }


def format_token_usage(usage: Dict[str, int]) -> str:
    """
    Format token usage for display.
    
    Args:
        usage: Token usage dictionary
    
    Returns:
        Formatted string
    """
    prompt = usage.get("prompt_tokens", 0)
    completion = usage.get("completion_tokens", 0)
    total = usage.get("total_tokens", 0)
    return f"Tokens - Prompt: {prompt:,}, Completion: {completion:,}, Total: {total:,}"
