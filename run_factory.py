"""Main entry point for running the NexusPrime factory."""

from __future__ import annotations

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

from nexusprime import build_nexus_factory


def run_simulation():
    """Run the NexusPrime factory with a sample input."""
    print("### BOOTING NEXUSPRIME FACTORY ###")
    app = build_nexus_factory()
    
    initial_state = {
        "messages": [HumanMessage(content="Build a secure Python calculator for production.")],
        "feedback_loop_count": 0
    }
    
    print(f"Input: {initial_state['messages'][0].content}")
    
    # Run the Graph
    final_state = app.invoke(initial_state)
    
    print("\n### FACTORY SHUTDOWN ###")
    print(f"Final Status: {final_state.get('current_status')}")
    print(f"Quality Score: {final_state.get('quality_score')}")
    print(f"Env Mode: {final_state.get('env_mode')}")


if __name__ == "__main__":
    run_simulation()
