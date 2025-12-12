"""State definition for NexusPrime factory."""

from __future__ import annotations

from typing import Annotated, Dict, List, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class NexusFactoryState(TypedDict):
    """
    Global State for the NexusPrime AI Software Factory.
    Passed between agents to maintain context and history.
    """
    messages: Annotated[List[BaseMessage], add_messages]  # Chat History
    spec_document: str                                    # The living SPEC.md content
    file_system_state: Dict[str, str]                     # Snapshot of key files (path -> content hash/summary)
    env_mode: Literal["DEV", "PROD"]                      # Current Environment
    current_status: str                                   # Observable status for Dashboard
    feedback_loop_count: int                              # Safety counter (max 5)
    quality_score: int                                    # 0-100 score from Council
    review_comments: str                                  # Feedback from Council
    memory_context: str                                   # Retrieved lessons from NexusMemory
    total_tokens: Dict[str, int]                          # Token Usage Tracking
    previous_code: str                                    # Code from previous version
    previous_reviews: List[Dict]                          # Previous reviews from Council
