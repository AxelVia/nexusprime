"""LangGraph construction for NexusPrime factory."""

from __future__ import annotations

from langgraph.graph import StateGraph, END

from .state import NexusFactoryState
from ..agents import ProductOwnerAgent, TechLeadAgent, DevSquadAgent, CouncilAgent
from ..config import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


def product_owner_node(state: NexusFactoryState) -> dict:
    """Product Owner node."""
    agent = ProductOwnerAgent()
    return agent.execute(state)


def tech_lead_node(state: NexusFactoryState) -> dict:
    """Tech Lead node."""
    agent = TechLeadAgent()
    return agent.execute(state)


def dev_squad_node(state: NexusFactoryState) -> dict:
    """Dev Squad node."""
    agent = DevSquadAgent()
    return agent.execute(state)


def council_node(state: NexusFactoryState) -> dict:
    """Council node."""
    agent = CouncilAgent()
    return agent.execute(state)


def route_council(state: NexusFactoryState) -> str:
    """
    Decide if code is approved or needs rework.
    
    Args:
        state: Current factory state
    
    Returns:
        Next node name: "approved", "rejected", or "failed"
    """
    settings = get_settings()
    score = state.get("quality_score", 0)
    env = state.get("env_mode", "DEV")
    loop_count = state.get("feedback_loop_count", 0)
    
    # Safety exit
    if loop_count > settings.max_feedback_loops:
        logger.warning(f"Maximum feedback loops ({settings.max_feedback_loops}) exceeded")
        return "failed"
    
    # Check quality thresholds
    if env == "DEV" and score > settings.dev_quality_threshold:
        logger.info(f"DEV approval: score {score} > {settings.dev_quality_threshold}")
        return "approved"
    elif env == "PROD" and score > settings.prod_quality_threshold:
        logger.info(f"PROD approval: score {score} > {settings.prod_quality_threshold}")
        return "approved"
    else:
        logger.info(f"Rejected: score {score} does not meet threshold for {env}")
        return "rejected"


def build_nexus_factory() -> StateGraph:
    """
    Build and compile the NexusPrime factory graph.
    
    Returns:
        Compiled StateGraph
    """
    logger.info("Building NexusPrime factory graph")
    
    workflow = StateGraph(NexusFactoryState)
    
    # Add nodes
    workflow.add_node("product_owner", product_owner_node)
    workflow.add_node("tech_lead", tech_lead_node)
    workflow.add_node("dev_squad", dev_squad_node)
    workflow.add_node("council", council_node)
    
    # Add edges
    workflow.set_entry_point("product_owner")
    workflow.add_edge("product_owner", "tech_lead")
    workflow.add_edge("tech_lead", "dev_squad")
    workflow.add_edge("dev_squad", "council")
    
    # Conditional routing from council
    workflow.add_conditional_edges(
        "council",
        route_council,
        {
            "approved": END,
            "rejected": "dev_squad",
            "failed": END
        }
    )
    
    compiled = workflow.compile()
    logger.info("NexusPrime factory graph compiled successfully")
    
    return compiled
