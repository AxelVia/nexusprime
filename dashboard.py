"""NexusPrime Dashboard - Real-time monitoring interface."""

from __future__ import annotations

import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURATION & STYLES ---
st.set_page_config(page_title="NEXUS PRIME // CONTROL CENTER", layout="wide", page_icon="💠")

# Futurism / Glassmorphism CSS
st.markdown("""
    <style>
    /* GLOBAL THEME */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #1a1a1a 0%, #000000 100%);
        color: #e0e0e0;
        font-family: 'Courier New', monospace;
    }
    
    /* NAV BAR */
    .saas-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background: rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .brand {
        font-size: 1.5em;
        font-weight: bold;
        color: #00ff88;
        letter-spacing: 2px;
    }
    .user-badge {
        background: #333;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8em;
    }
    
    /* CARDS (Glass Effect) */
    .nexus-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s;
    }
    .nexus-card:hover { border-color: #00ff88; }
    
    /* METRICS */
    .metric-value {
        font-size: 2.2em;
        font-weight: 700;
        color: #fff;
    }
    .metric-label {
        font-size: 0.8em;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* LOG CONSOLE */
    .console-box {
        background-color: #000;
        border: 1px solid #333;
        border-radius: 5px;
        padding: 15px;
        font-family: 'Consolas', monospace;
        color: #0f0;
        height: 350px;
        overflow-y: auto;
    }
    .log-entry { margin-bottom: 5px; border-bottom: 1px solid #111; padding-bottom: 2px;} 
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="saas-header">
    <div class="brand">NEXUS PRIME <span style="font-size:0.6em; color:#fff;">// AI SOFTWARE FACTORY</span></div>
    <div class="user-badge">User: AXEL | Plan: PRO</div>
</div>
""", unsafe_allow_html=True)

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

def get_status_icon(text):
    if "Product Owner" in text: return ("🕵️", "Conception", 10)
    if "Tech Lead" in text: return ("🌐", "Architecture", 35)
    if "Dev Squad" in text: return ("⚡", "Development", 65)
    if "Council" in text: return ("🛡️", "Auditing", 90)
    return ("⏳", "Standby", 0)

# --- AUTO-REFRESH ---
# Refresh every 2 seconds (2000ms)
st_autorefresh(interval=2000, limit=None, key="nexus_refresh")

# --- MAIN DASHBOARD ---

# --- NEW PROJECT INPUT ---
with st.expander("🚀 Lancer un Nouveau Projet", expanded=True):
    with st.form("new_project_form"):
        user_prompt = st.text_area("Décrivez votre besoin :", height=100, placeholder="Ex: Créer une API FastAPI pour gérer des produits...")
        submitted = st.form_submit_button("Démarrer l'Usine")
        
        if submitted and user_prompt:
            try:
                with open("request.json", "w", encoding="utf-8") as f:
                    json.dump({"prompt": user_prompt}, f)
                st.success("Requete envoyée au Daemon NexusPrime ! (L'usine va démarrer dans quelques secondes...)")
            except Exception as e:
                st.error(f"⚠️ Failed to save request: {e}")

# Load current status and memory
status = load_status()
memory = load_memory()
        # TABS
        tab1, tab2, tab3 = st.tabs(["📊 SYSTEM MONITOR", "🧠 NEURAL MEMORY", "💳 TOKEN USAGE"])
        
# --- TAB 1: MONITOR ---
with tab1:
    # METRICS ROW
    col1, col2, col3, col4 = st.columns(4)
    
    raw_status = status.get('current_status', 'Offline') if status else 'Offline'
    icon, short_status, progress_val = get_status_icon(raw_status)
    
    with col1:
        st.markdown(f"""
        <div class="nexus-card">
            <div class="metric-label">ACTIVE MODULE</div>
            <div class="metric-value" style="color:#00ff88; font-size:1.5em;">{icon} {short_status}</div>
            <div style="height:4px; background:#333; margin-top:10px;"><div style="width:{progress_val}%; height:100%; background:#00ff88;"></div></div>
        </div>""", unsafe_allow_html=True)

    score = status.get('quality_score', 0) if status else 0
    with col2:
        st.markdown(f"""<div class="nexus-card"><div class="metric-label">QUALITY SCORE</div><div class="metric-value">{score}/100</div></div>""", unsafe_allow_html=True)

    loop = status.get('feedback_loop_count', 0) if status else 0
    with col3:
        st.markdown(f"""<div class="nexus-card"><div class="metric-label">LOOPS</div><div class="metric-value">{loop}</div></div>""", unsafe_allow_html=True)

    env = status.get('env_mode', 'N/A') if status else 'N/A'
    with col4:
        st.markdown(f"""<div class="nexus-card"><div class="metric-label">ENV MODE</div><div class="metric-value" style="color:#00b8ff">{env}</div></div>""", unsafe_allow_html=True)

    # CONSOLE AREA
    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.markdown("### 🖥️ LIVE TERMINAL")
        log_content = ""
        if status:
            spec_excerpt = status.get('spec_excerpt', '')
            last_msg = status.get('last_message', '')
            log_content += f"<div class='log-entry'><span style='color:#555'>[{datetime.now().strftime('%H:%M:%S')}]</span> SYSTEM: Processing Input...</div>"
            log_content += f"<div class='log-entry'><span style='color:#555'>[{datetime.now().strftime('%H:%M:%S')}]</span> USER: {last_msg}</div>"
            if spec_excerpt:
                log_content += f"<div style='color:#888; margin-top:10px; font-size:0.8em; border-left:2px solid #333; padding-left:10px;'>{spec_excerpt}</div>"
        
        st.markdown(f"""<div class="console-box">{log_content}<div style='color:#00ff88; animation: blink 1s infinite;'>_</div></div>""", unsafe_allow_html=True)
    
    with c_right:
        st.markdown("### 📂 WORKSPACE")
        if os.path.exists("workspace"):
            try:
                files = os.listdir("workspace")
                for f in files:
                    st.code(f"📄 {f}")
            except Exception as e:
                st.warning(f"Could not list workspace files: {e}")

# --- TAB 2: MEMORY ---
with tab2:
    st.subheader("Persistent Learning (RAG)")
    if memory and memory.get("lessons"):
        for l in reversed(memory["lessons"]):
            st.success(f"TOPIC: {l['topic']}")
            st.json(l)
    else:
        st.info("No memories stored yet.")

# --- TAB 3: TOKEN USAGE (REAL) ---
with tab3:
    st.subheader("💰 Resource Consumption (Real-Time)")
    
    tokens = status.get('total_tokens', {}) if status else {}
    total = tokens.get('total_tokens', 0)
    prompt = tokens.get('prompt_tokens', 0)
    completion = tokens.get('completion_tokens', 0)
    
    # Simulated cost calculation (approx for Gemini)
    cost = (prompt * 0.0000005) + (completion * 0.0000015)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tokens", f"{total:,}")
    m2.metric("Prompt Tokens", f"{prompt:,}")
    m3.metric("Completion Tokens", f"{completion:,}")
    m4.metric("Est. Cost", f"${cost:.6f}")
    
    st.progress(min(total / 1000000, 1.0)) # Max 1M context bar
    st.caption("Usage resets on factory restart.")
