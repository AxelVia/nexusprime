"""NexusPrime Dashboard - Real-time monitoring interface with Multi-LLM visualization."""

from __future__ import annotations

import streamlit as st
import json
import os
import sys
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import UI components
from nexusprime.ui import (
    get_base_styles,
    render_header,
    render_metrics_card,
    render_progress_pipeline,
    render_active_agent,
    render_council_section,
    render_terminal,
)
from nexusprime.ui.components import render_workspace_files
from nexusprime.ui.animations import get_animation_styles

# --- CONFIGURATION ---
st.set_page_config(
    page_title="NEXUSPRIME // MULTI-LLM CONTROL CENTER",
    layout="wide",
    page_icon="🔮"
)

# Apply styles
st.markdown(get_base_styles(), unsafe_allow_html=True)
st.markdown(get_animation_styles(), unsafe_allow_html=True)

# --- AUTO-REFRESH ---
# Refresh every 2 seconds
st_autorefresh(interval=2000, limit=1000, key="nexus_refresh")

# --- DATA HELPERS ---
def load_status():
    """Load status from JSON file with error handling."""
    if os.path.exists("status.json"):
        try:
            with open("status.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("⚠️ status.json is corrupted. Please restart the factory.")
            return None
        except Exception as e:
            st.error(f"⚠️ Failed to load status.json: {e}")
            return None
    return None


def load_memory():
    """Load memory from JSON file with error handling."""
    if os.path.exists("nexus_memory.json"):
        try:
            with open("nexus_memory.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.warning("⚠️ nexus_memory.json is corrupted. Showing empty memory.")
            return {"lessons": []}
        except Exception as e:
            st.warning(f"⚠️ Failed to load memory: {e}")
            return {"lessons": []}
    return {"lessons": []}


def parse_agent_info(status_text: str) -> tuple[str, str, str, int]:
    """
    Parse status text to extract agent info.
    
    Args:
        status_text: Status string from state
    
    Returns:
        Tuple of (agent_name, model, status_message, progress_percent)
    """
    # Default values
    agent_name = "Standby"
    model = "N/A"
    status_msg = "Waiting for task..."
    progress = 0
    
    if not status_text:
        return agent_name, model, status_msg, progress
    
    # Parse agent name and determine model
    if "Product Owner" in status_text:
        agent_name = "Product Owner"
        model = "Claude Sonnet 4"
        status_msg = "Analyzing requirements and generating specification..."
        progress = 25
    elif "Tech Lead" in status_text:
        agent_name = "Tech Lead"
        model = "Gemini 2.5 Pro"
        status_msg = "Setting up environment and retrieving memory context..."
        progress = 50
    elif "Dev Squad" in status_text:
        agent_name = "Dev Squad"
        model = "Claude Sonnet 4"
        status_msg = "Generating code based on specifications..."
        progress = 75
    elif "Council" in status_text:
        agent_name = "Council"
        model = "Multi-LLM (Grok + Gemini + Claude)"
        status_msg = "Conducting multi-LLM review with debate system..."
        progress = 90
    
    return agent_name, model, status_msg, progress


def parse_council_data(status: dict) -> tuple:
    """
    Parse council review data from status.
    
    Args:
        status: Status dictionary
    
    Returns:
        Tuple of (judges_list, arbitrator_dict, previous_score)
    """
    # Try to parse council report if available
    council_report = status.get("council_report", "")
    quality_score = status.get("quality_score", 0)
    previous_reviews = status.get("previous_reviews", [])
    
    judges = None
    arbitrator = None
    previous_score = None
    
    if quality_score > 0:
        # Use previous_reviews if available, otherwise parse from report
        if previous_reviews:
            judges = []
            for review in previous_reviews:
                reviewer = review.get("reviewer", "Unknown")
                score = review.get("score", 0)
                verdict = "APPROVE" if score > 75 else "NEEDS_WORK" if score > 50 else "REJECT"
                
                judges.append({
                    "name": reviewer,
                    "model": review.get("model", "unknown"),
                    "score": score,
                    "verdict": verdict,
                    "concerns": review.get("concerns", [])
                })
        else:
            # Fallback to placeholder data
            judges = [
                {"name": "GPT-5", "model": "gpt-5", "score": quality_score - 2, "verdict": "APPROVE" if quality_score > 75 else "REJECT", "concerns": []},
                {"name": "Gemini", "model": "gemini-2.5-pro", "score": quality_score, "verdict": "APPROVE" if quality_score > 75 else "REJECT", "concerns": []},
                {"name": "Claude", "model": "claude-sonnet-4", "score": quality_score + 2, "verdict": "APPROVE" if quality_score > 75 else "NEEDS_WORK", "concerns": []},
            ]
        
        # Calculate previous score if available
        feedback_loop = status.get("feedback_loop_count", 0)
        if feedback_loop > 1:
            # Estimate previous score (in real scenario, this would be stored)
            previous_score = quality_score - 5  # Simple estimation
        
        # Extract arbitration reasoning from report
        reasoning = "Synthesized review from multiple independent judges."
        if council_report and "FINAL ARBITRATION" in council_report:
            # Try to extract reasoning from report
            lines = council_report.split('\n')
            for i, line in enumerate(lines):
                if "Reasoning:" in line:
                    reasoning = line.split("Reasoning:", 1)[1].strip()
                    break
        
        arbitrator = {
            "score": quality_score,
            "reasoning": reasoning,
            "verdict": "APPROVE" if quality_score > 75 else "NEEDS_WORK"
        }
    
    return judges, arbitrator, previous_score


def build_log_entries(status: dict) -> list:
    """
    Build log entries from status data.
    
    Args:
        status: Status dictionary
    
    Returns:
        List of (timestamp, level, message) tuples
    """
    logs = []
    current_time = datetime.now().strftime("%H:%M:%S")
    
    if not status:
        return logs
    
    # Add current status as log
    current_status = status.get("current_status", "")
    if current_status:
        logs.append((current_time, "info", current_status))
    
    # Add spec excerpt if available
    spec_excerpt = status.get("spec_excerpt", "")
    if spec_excerpt:
        logs.append((current_time, "success", f"📝 Spec generated: {spec_excerpt[:100]}..."))
    
    # Add quality score if available
    quality_score = status.get("quality_score", 0)
    if quality_score > 0:
        level = "success" if quality_score > 75 else "warning"
        logs.append((current_time, level, f"⚖️ Quality Score: {quality_score}/100"))
    
    # Add last message
    last_msg = status.get("last_message", "")
    if last_msg:
        logs.append((current_time, "info", f"💬 User: {last_msg[:80]}..."))
    
    return logs


# --- MAIN DASHBOARD ---

# Render header
st.markdown(render_header(), unsafe_allow_html=True)

# --- NEW PROJECT INPUT ---
with st.expander("🚀 Launch New Project", expanded=False):
    st.markdown("""
    <div style="margin-bottom: 15px; color: #94a3b8; font-size: 0.9em;">
        Describe your project requirements. The Multi-LLM factory will analyze, architect, 
        develop, and review your project automatically.
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("new_project_form"):
        user_prompt = st.text_area(
            "Project Description:",
            height=120,
            placeholder="Example: Create a REST API with FastAPI for managing a todo list with SQLite database, authentication, and proper error handling..."
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            env_mode = st.selectbox("Environment:", ["DEV", "PROD"])
        with col2:
            submitted = st.form_submit_button("🚀 Launch Factory", use_container_width=True)
        
        if submitted and user_prompt:
            try:
                request_data = {
                    "prompt": user_prompt,
                    "env_mode": env_mode,
                    "timestamp": datetime.now().isoformat()
                }
                with open("request.json", "w", encoding="utf-8") as f:
                    json.dump(request_data, f)
                st.success("✅ Request submitted! The factory will start processing in a few seconds...")
            except Exception as e:
                st.error(f"⚠️ Failed to save request: {e}")

st.markdown("<br>", unsafe_allow_html=True)

# Load current status and memory
status = load_status()
memory = load_memory()

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 SYSTEM MONITOR",
    "⚖️ COUNCIL REVIEW",
    "🧠 NEURAL MEMORY",
    "💳 TOKEN USAGE"
])

# --- TAB 1: SYSTEM MONITOR ---
with tab1:
    # Determine current pipeline step
    current_status = status.get("current_status", "") if status else ""
    
    # Map status to pipeline step
    pipeline_step = "input"
    if "Product Owner" in current_status:
        pipeline_step = "po"
    elif "Tech Lead" in current_status:
        pipeline_step = "tech"
    elif "Dev Squad" in current_status:
        pipeline_step = "dev"
    elif "Council" in current_status:
        pipeline_step = "council"
    
    # Render pipeline
    st.markdown(
        render_progress_pipeline(pipeline_step),
        unsafe_allow_html=True
    )
    
    # Parse agent info
    agent_name, model, status_msg, progress = parse_agent_info(current_status)
    
    # Active Agent Section
    st.markdown(
        render_active_agent(agent_name, model, status_msg, progress),
        unsafe_allow_html=True
    )
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    score = status.get("quality_score", 0) if status else 0
    score_color = "#10b981" if score > 75 else "#f59e0b" if score > 50 else "#ef4444"
    
    with col1:
        st.markdown(
            render_metrics_card(
                "Quality Score",
                f"{score}/100",
                "⭐",
                progress=score,
                color=score_color
            ),
            unsafe_allow_html=True
        )
    
    loop_count = status.get("feedback_loop_count", 0) if status else 0
    with col2:
        st.markdown(
            render_metrics_card(
                "Feedback Loops",
                f"{loop_count}/5",
                "🔄",
                progress=min(100, (loop_count / 5) * 100),  # Cap at 100%
                color="#6366f1"
            ),
            unsafe_allow_html=True
        )
    
    env_mode = status.get("env_mode", "N/A") if status else "N/A"
    env_color = "#8b5cf6" if env_mode == "PROD" else "#10b981"
    with col3:
        st.markdown(
            render_metrics_card(
                "Environment",
                env_mode,
                "🌍",
                color=env_color
            ),
            unsafe_allow_html=True
        )
    
    # Token preview in metric
    tokens = status.get("total_tokens", {}) if status else {}
    total_tokens = tokens.get("total_tokens", 0)
    with col4:
        st.markdown(
            render_metrics_card(
                "Total Tokens",
                f"{total_tokens:,}",
                "🪙",
                color="#f59e0b"
            ),
            unsafe_allow_html=True
        )
    
    # Terminal and Workspace
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""
        <div class="nexus-card">
            <div class="card-title">
                <span class="card-icon">🖥️</span>
                LIVE TERMINAL
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        logs = build_log_entries(status)
        st.markdown(render_terminal(logs), unsafe_allow_html=True)
    
    with col_right:
        st.markdown(render_workspace_files(), unsafe_allow_html=True)

# --- TAB 2: COUNCIL REVIEW ---
with tab2:
    st.markdown("""
    <div style="margin-bottom: 20px; padding: 20px; background: rgba(99, 102, 241, 0.1); 
                border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.3);">
        <h3 style="margin: 0 0 10px 0; color: #6366f1;">⚖️ Multi-LLM Council Review System</h3>
        <p style="margin: 0; color: #94a3b8; font-size: 0.9em;">
            Three independent AI judges (Grok, Gemini, Claude) review every output. 
            Claude then arbitrates to provide a final definitive quality score.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    judges, arbitrator, previous_score = parse_council_data(status if status else {})
    st.markdown(
        render_council_section(judges, arbitrator, previous_score),
        unsafe_allow_html=True
    )
    
    # Show detailed report if available
    if status and status.get("council_report"):
        with st.expander("📋 View Detailed Council Report"):
            st.code(status["council_report"], language="text")

# --- TAB 3: MEMORY ---
with tab3:
    st.markdown("""
    <div class="nexus-card">
        <div class="card-title">
            <span class="card-icon">🧠</span>
            PERSISTENT LEARNING (RAG System)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if memory and memory.get("lessons"):
        st.info(f"**{len(memory['lessons'])} lessons stored** in neural memory")
        
        for idx, lesson in enumerate(reversed(memory["lessons"][-10:])):  # Show last 10
            with st.expander(f"Lesson {len(memory['lessons']) - idx}: {lesson.get('topic', 'Unknown')}", expanded=False):
                st.json(lesson)
    else:
        st.info("🔍 No memories stored yet. The system will learn from successful projects.")

# --- TAB 4: TOKEN USAGE ---
with tab4:
    st.markdown("""
    <div class="nexus-card">
        <div class="card-title">
            <span class="card-icon">💰</span>
            RESOURCE CONSUMPTION (Real-Time)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tokens = status.get("total_tokens", {}) if status else {}
    total = tokens.get("total_tokens", 0)
    prompt = tokens.get("prompt_tokens", 0)
    completion = tokens.get("completion_tokens", 0)
    
    # Estimated cost calculation
    # These are approximate costs for GitHub Copilot API
    cost = (prompt * 0.000002) + (completion * 0.000008)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            render_metrics_card(
                "Total Tokens",
                f"{total:,}",
                "🪙",
                color="#6366f1"
            ),
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            render_metrics_card(
                "Input Tokens",
                f"{prompt:,}",
                "📥",
                color="#8b5cf6"
            ),
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            render_metrics_card(
                "Output Tokens",
                f"{completion:,}",
                "📤",
                color="#10b981"
            ),
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            render_metrics_card(
                "Est. Cost",
                f"${cost:.4f}",
                "💵",
                color="#f59e0b"
            ),
            unsafe_allow_html=True
        )
    
    # Progress bar for context window
    st.markdown("<br>", unsafe_allow_html=True)
    progress_pct = min((total / 1000000) * 100, 100)
    st.progress(progress_pct / 100)
    st.caption(f"📊 Context usage: {total:,} / 1,000,000 tokens ({progress_pct:.1f}%)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Cost breakdown by model
    st.markdown("""
    <div class="nexus-card">
        <div class="card-title">
            <span class="card-icon">💎</span>
            MODEL COST BREAKDOWN
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    | Model | Usage | Approx. Cost/1M Tokens |
    |-------|-------|------------------------|
    | Claude Sonnet 4 | Product Owner, Dev Squad, Council | $3-15 |
    | Gemini 2.5 Pro | Tech Lead, Council | $1.25-5 |
    | Grok 3 | Council | $2-10 |
    
    💡 **Tip**: DEV mode uses fewer tokens than PROD mode (less strict validation)
    """)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.8em; padding: 20px; 
            border-top: 1px solid #2d2d3a;">
    🔮 NexusPrime Multi-LLM Factory | Powered by Claude, Gemini & Grok via GitHub Copilot
</div>
""", unsafe_allow_html=True)
