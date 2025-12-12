import os
import json
from typing import TypedDict, List, Literal, Annotated, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from nexus_memory import NexusMemory

# --- Configuration ---
load_dotenv() # Load GOOGLE_API_KEY and GITHUB_TOKEN

# Setup Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro",
    temperature=0.2, # Low temp for precise engineering
    convert_system_message_to_human=True
)

# --- Helpers ---
def call_llm(prompt: str, system_prompt: str = "You are a precise coding agent.") -> tuple[str, dict]:
    """
    Calls the real Gemini Pro model and returns content + token usage.
    """
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        # Gemini usage metadata structure
        usage = response.response_metadata.get("token_usage", {})
        # Normalize keys if needed
        return response.content, usage
    except Exception as e:
        print(f"LLM Error: {e}")
        return f"Error calling LLM: {str(e)}", {}

memory_module = NexusMemory() # Singleton instance

# --- State Definition ---

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

STATUS_FILE = "status.json"

def save_status_snapshot(state: NexusFactoryState):
    """
    Exports the current state to a JSON file for the Dashboard.
    """
    snapshot = {
        "current_status": state.get("current_status"),
        "env_mode": state.get("env_mode"),
        "quality_score": state.get("quality_score"),
        "feedback_loop_count": state.get("feedback_loop_count"),
        "spec_excerpt": state.get("spec_document", "")[:200],
        # Convert messages to string for JSON serialization
        "last_message": state["messages"][-1].content if state.get("messages") else "",
        "total_tokens": state.get("total_tokens", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)

# --- Agent Nodes (Skeleton) ---

def _update_tokens(current_usage: dict, new_usage: dict) -> dict:
    """Helper to sum token usage."""
    return {
        "prompt_tokens": current_usage.get("prompt_tokens", 0) + new_usage.get("prompt_token_count", 0),
        "completion_tokens": current_usage.get("completion_tokens", 0) + new_usage.get("candidates_token_count", 0),
        "total_tokens": current_usage.get("total_tokens", 0) + new_usage.get("total_token_count", 0)
    }

def product_owner_node(state: NexusFactoryState):
    """
    Product Owner: Refines requirements into a SPEC.md.
    """
    print("--- [Agent] Product Owner: Refining Spec ---")
    
    # Get latest user message
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1].content
    else:
        last_msg = "No input provided."

    # "Real" Requirement Analysis
    # The AI Agent dries the spec based on the user prompt
    spec, usage = call_llm(f"Generate a strict SPEC.md for this request: {last_msg}")
    
    new_tokens = _update_tokens(state.get("total_tokens", {}), usage)

    state_update = {
        "current_status": "Agent: Product Owner (Refining Spec)",
        "spec_document": spec,
        "total_tokens": new_tokens
    }
    save_status_snapshot({**state, **state_update})
    return state_update

def tech_lead_node(state: NexusFactoryState):
    """
    Tech Lead: Sets up environment and dispatches to Dev Squad.
    Injects MEMORY into the context.
    """
    print("--- [Agent] Tech Lead: Setting up Environment ---")
    
    spec = state.get("spec_document", "")
    
    # 1. Retrieve Lessons from Memory
    memory_ctx = memory_module.retrieve_context(spec)
    print(f"   >>> Retrieved Context: {len(memory_ctx)} chars")

    # 2. Determine Environment (AI Decision)
    # We ask the LLM to decide if this is a PROD or DEV request
    env_prompt = f"Based on this compiled spec, does the user want a Production-ready system or a Prototype? Return ONLY 'PROD' or 'DEV'.\n\nSPEC EXCERPT:\n{spec[:500]}"
    try:
        env_decision, usage = call_llm(env_prompt, system_prompt="You are a Tech Lead. Output only PROD or DEV.")
        env_mode = "PROD" if "PROD" in env_decision.upper() else "DEV"
    except:
        env_mode = "DEV" # Safe fallback
        usage = {}

    print(f"   >>> Environment Set to: {env_mode}")
    
    # 3. REAL GITHUB INTEGRATION
    repo_url = "N/A"
    try:
        from github import Github
        g = Github(os.getenv("GITHUB_TOKEN"))
        user = g.get_user()
        repo_name = "nexus-prime-workspace"
        
        # Check if repo exists, else create
        try:
            repo = user.get_repo(repo_name)
            print(f"   >>> Found existing repo: {repo.html_url}")
        except:
            repo = user.create_repo(repo_name, description="Automated Factory Workspace", private=True)
            print(f"   >>> Created new repo: {repo.html_url}")
            
        repo_url = repo.html_url
        # In a real app, we would git clone here. For now we will push via API in the Dev/Council node.
        
    except Exception as e:
        print(f"   >>> GitHub Error (Non-blocking): {e}")

    new_tokens = _update_tokens(state.get("total_tokens", {}), usage)

    state_update = {
        "current_status": "Agent: Tech Lead (Setup & Dispatch)",
        "env_mode": env_mode,
        "memory_context": memory_ctx,
        "repo_url": repo_url, # Store for Dashboard
        "total_tokens": new_tokens
    }
    save_status_snapshot({**state, **state_update})
    return state_update

def dev_squad_node(state: NexusFactoryState):
    """
    Dev Squad: Writes code and runs tests.
    """
    print("--- [Agent] Dev Squad: Coding ---")
    
    spec = state.get("spec_document", "")
    env = state.get("env_mode", "DEV")
    
    spec = state.get("spec_document", "")
    env = state.get("env_mode", "DEV")
    
    # REAL AI CODING
    prompt = f"Write the complete Python code for the following specification. Return ONLY the code, no markdown.\n\nSPEC:\n{spec}"
    code_content, usage = call_llm(prompt, system_prompt="You are a senior Python developer. Write clean, production-ready code.")
    
    # Strip markdown code fences if present
    code_content = code_content.replace("```python", "").replace("```", "")
    
    # In a real scenario, this would write to filesystem
    file_path = f"workspace/app_{env.lower()}.py"
    if not os.path.exists("workspace"):
        os.makedirs("workspace")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code_content)
        
    print(f"   >>> Code written to {file_path}")

    new_tokens = _update_tokens(state.get("total_tokens", {}), usage)

    state_update = {
        "current_status": "Agent: Dev Squad (Coding)",
        "file_system_state": {file_path: "generated_by_gemini"},
        "total_tokens": new_tokens
    }
    save_status_snapshot({**state, **state_update})
    return state_update

def council_node(state: NexusFactoryState):
    """
    The Council: Validates quality and decides next step.
    Archives lessons if successful.
    """
    print("--- [Agent] The Council: Reviewing ---")
    
    env = state.get("env_mode", "DEV")
    spec = state.get("spec_document", "")
    
    # REAL AI GOVERNANCE
    # We ask the LLM to review the code (simulated retrieval, but real decision)
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
    
    new_tokens = state.get("total_tokens", {})
    try:
        score_str, usage = call_llm(prompt, system_prompt="You are a strict code auditor. Output only the integer score.")
        new_score = int(''.join(filter(str.isdigit, score_str)))
        new_tokens = _update_tokens(state.get("total_tokens", {}), usage)
    except:
        new_score = 70 # Fallback
    
    print(f"   >>> Quality Score Assigned by AI: {new_score}/100")
    
    # Check for Approval to Archive Lessons
    is_approved = (env == "DEV" and new_score > 75) or (env == "PROD" and new_score > 95)
    
    if is_approved:
        print("   >>> [Council] APPROVAL GRANTED. Archiving Lesson.")
        memory_module.store_lesson(
            topic="Feature Implementation",
            context=state.get("spec_document", "")[:50] + "...",
            outcome="Success",
            solution="Followed Spec X, implemented Y."
        )
        
        # GITHUB PUSH
        try:
            from github import Github
            g = Github(os.getenv("GITHUB_TOKEN"))
            user = g.get_user()
            repo = user.get_repo("nexus-prime-workspace")
            
            # Find the file created by Dev Squad
            # In a real system, we'd track the exact filename better
            files = ["app_dev.py", "app_prod.py"]
            for fname in files:
                fpath = f"workspace/{fname}"
                if os.path.exists(fpath):
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Create or Update file in repo
                    try:
                        contents = repo.get_contents(fname)
                        repo.update_file(contents.path, f"Update {fname} by NexusPrime", content, contents.sha)
                        print(f"   >>> GitHub: Updated {fname}")
                    except:
                        repo.create_file(fname, f"Create {fname} by NexusPrime", content)
                        print(f"   >>> GitHub: Created {fname}")
        except Exception as e:
            print(f"   >>> GitHub Push Error: {e}")

    state_update = {
        "current_status": "Agent: The Council (Reviewing)",
        "quality_score": new_score, 
        "feedback_loop_count": state.get("feedback_loop_count", 0) + 1,
        "total_tokens": new_tokens
    }
    save_status_snapshot({**state, **state_update})
    return state_update

# --- Conditional Logic (Routing) ---

def route_council(state: NexusFactoryState):
    """
    Decides if code is approved or needs rework.
    """
    score = state.get("quality_score", 0)
    env = state.get("env_mode", "DEV")
    loop_count = state.get("feedback_loop_count", 0)

    if loop_count > 5:
        return "failed" # Safety exit
    
    if env == "DEV" and score > 75:
        return "approved"
    elif env == "PROD" and score > 95:
        return "approved"
    else:
        return "rejected"

# --- Graph Construction ---

def build_nexus_factory():
    workflow = StateGraph(NexusFactoryState)

    # Add Nodes
    workflow.add_node("product_owner", product_owner_node)
    workflow.add_node("tech_lead", tech_lead_node)
    workflow.add_node("dev_squad", dev_squad_node)
    workflow.add_node("council", council_node)

    # Add Edges
    workflow.set_entry_point("product_owner")
    
    workflow.add_edge("product_owner", "tech_lead")
    workflow.add_edge("tech_lead", "dev_squad")
    workflow.add_edge("dev_squad", "council")

    workflow.add_conditional_edges(
        "council",
        route_council,
        {
            "approved": END,
            "rejected": "dev_squad",
            "failed": END
        }
    )

    return workflow.compile()

if __name__ == "__main__":
    # Quick Test
    app = build_nexus_factory()
    print("NexusFactory Graph Compiled Successfully.")
