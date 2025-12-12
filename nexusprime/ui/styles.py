"""Style constants and CSS for NexusPrime dashboard."""

# Modern SaaS Dark Theme Color Palette
COLORS = {
    "bg_primary": "#0a0a0f",        # Main background - very dark
    "bg_secondary": "#12121a",       # Secondary background
    "bg_card": "#1a1a2e",            # Card backgrounds
    "accent_primary": "#6366f1",     # Indigo - primary accent
    "accent_secondary": "#8b5cf6",   # Violet
    "accent_success": "#10b981",     # Emerald green
    "accent_warning": "#f59e0b",     # Amber orange
    "accent_error": "#ef4444",       # Red
    "text_primary": "#f8fafc",       # Primary text - almost white
    "text_secondary": "#94a3b8",     # Secondary text - slate gray
    "border": "#2d2d3a",             # Border color
    "glow": "rgba(99, 102, 241, 0.4)", # Glow effect for accent
    "glow_success": "rgba(16, 185, 129, 0.4)",
    "glow_warning": "rgba(245, 158, 11, 0.4)",
}


def get_base_styles() -> str:
    """
    Generate base CSS styles for the dashboard.
    
    Returns:
        CSS string with all base styles
    """
    return f"""
    <style>
    /* ===== GLOBAL THEME ===== */
    .stApp {{
        background: linear-gradient(135deg, {COLORS['bg_primary']} 0%, {COLORS['bg_secondary']} 100%);
        color: {COLORS['text_primary']};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* Hide default Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* ===== HEADER ===== */
    .nexus-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 30px;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-bottom: 1px solid {COLORS['border']};
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }}
    
    .brand-logo {{
        font-size: 1.8em;
        font-weight: 800;
        background: linear-gradient(135deg, {COLORS['accent_primary']}, {COLORS['accent_secondary']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 2px;
        text-shadow: 0 0 30px {COLORS['glow']};
    }}
    
    .brand-subtitle {{
        font-size: 0.5em;
        color: {COLORS['text_secondary']};
        letter-spacing: 3px;
        font-weight: 400;
        display: block;
        margin-top: 5px;
    }}
    
    .multi-llm-badge {{
        display: inline-block;
        background: linear-gradient(135deg, {COLORS['accent_primary']}, {COLORS['accent_secondary']});
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.75em;
        font-weight: 600;
        margin-left: 15px;
        box-shadow: 0 4px 15px {COLORS['glow']};
        animation: pulse-glow 2s ease-in-out infinite;
    }}
    
    .status-indicator {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.9em;
        color: {COLORS['text_secondary']};
    }}
    
    .status-dot {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: {COLORS['accent_success']};
        box-shadow: 0 0 10px {COLORS['glow_success']};
        animation: pulse 2s ease-in-out infinite;
    }}
    
    /* ===== CARDS ===== */
    .nexus-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }}
    
    .nexus-card:hover {{
        border-color: {COLORS['accent_primary']};
        box-shadow: 0 8px 40px {COLORS['glow']};
        transform: translateY(-2px);
    }}
    
    .card-title {{
        font-size: 1.1em;
        font-weight: 600;
        color: {COLORS['text_primary']};
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    
    .card-icon {{
        font-size: 1.3em;
    }}
    
    /* ===== METRICS ===== */
    .metric-container {{
        text-align: center;
    }}
    
    .metric-value {{
        font-size: 2.5em;
        font-weight: 800;
        color: {COLORS['text_primary']};
        line-height: 1.2;
        margin: 10px 0;
    }}
    
    .metric-label {{
        font-size: 0.75em;
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 500;
    }}
    
    .metric-progress {{
        height: 6px;
        background: {COLORS['bg_secondary']};
        border-radius: 3px;
        margin-top: 12px;
        overflow: hidden;
    }}
    
    .metric-progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, {COLORS['accent_primary']}, {COLORS['accent_secondary']});
        border-radius: 3px;
        transition: width 0.5s ease;
        box-shadow: 0 0 10px {COLORS['glow']};
    }}
    
    /* ===== PIPELINE ===== */
    .pipeline {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        margin-bottom: 25px;
    }}
    
    .pipeline-step {{
        flex: 1;
        text-align: center;
        position: relative;
        padding: 15px 10px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }}
    
    .pipeline-step.active {{
        background: rgba(99, 102, 241, 0.15);
        border: 2px solid {COLORS['accent_primary']};
        box-shadow: 0 0 20px {COLORS['glow']};
    }}
    
    .pipeline-step.completed {{
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid {COLORS['accent_success']};
    }}
    
    .pipeline-step.pending {{
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid {COLORS['border']};
        opacity: 0.5;
    }}
    
    .pipeline-icon {{
        font-size: 1.5em;
        margin-bottom: 8px;
    }}
    
    .pipeline-label {{
        font-size: 0.8em;
        font-weight: 500;
        color: {COLORS['text_secondary']};
    }}
    
    .pipeline-step.active .pipeline-label {{
        color: {COLORS['accent_primary']};
        font-weight: 600;
    }}
    
    .pipeline-arrow {{
        color: {COLORS['border']};
        font-size: 1.5em;
        margin: 0 5px;
    }}
    
    /* ===== ACTIVE AGENT ===== */
    .agent-card {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.05));
        border: 1px solid {COLORS['accent_primary']};
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 0 30px {COLORS['glow']};
    }}
    
    .agent-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }}
    
    .agent-name {{
        font-size: 1.3em;
        font-weight: 700;
        color: {COLORS['text_primary']};
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    
    .agent-model {{
        font-size: 0.85em;
        color: {COLORS['text_secondary']};
        background: rgba(255, 255, 255, 0.05);
        padding: 6px 14px;
        border-radius: 12px;
        border: 1px solid {COLORS['border']};
    }}
    
    .agent-status {{
        font-size: 0.9em;
        color: {COLORS['text_secondary']};
        margin-bottom: 15px;
    }}
    
    /* ===== COUNCIL ===== */
    .council-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-bottom: 20px;
    }}
    
    .judge-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .judge-card:hover {{
        border-color: {COLORS['accent_primary']};
        transform: translateY(-5px);
    }}
    
    .judge-name {{
        font-size: 1.1em;
        font-weight: 600;
        margin-bottom: 10px;
        color: {COLORS['text_primary']};
    }}
    
    .judge-model {{
        font-size: 0.75em;
        color: {COLORS['text_secondary']};
        margin-bottom: 15px;
    }}
    
    .judge-score {{
        font-size: 2em;
        font-weight: 800;
        color: {COLORS['accent_primary']};
        margin: 15px 0;
    }}
    
    .score-circle {{
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 4px solid {COLORS['border']};
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 15px auto;
        font-size: 1.8em;
        font-weight: 800;
        background: rgba(255, 255, 255, 0.05);
    }}
    
    .verdict-badge {{
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: 600;
        text-transform: uppercase;
    }}
    
    .verdict-approve {{
        background: {COLORS['accent_success']};
        color: white;
        box-shadow: 0 0 15px {COLORS['glow_success']};
    }}
    
    .verdict-reject {{
        background: {COLORS['accent_error']};
        color: white;
    }}
    
    .verdict-pending {{
        background: {COLORS['accent_warning']};
        color: white;
        box-shadow: 0 0 15px {COLORS['glow_warning']};
    }}
    
    .arbitrator-card {{
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
        border: 2px solid {COLORS['accent_primary']};
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 0 30px {COLORS['glow']};
    }}
    
    /* ===== TERMINAL ===== */
    .terminal-container {{
        background: #000000;
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px;
        font-family: 'Monaco', 'Courier New', monospace;
        color: {COLORS['accent_success']};
        height: 400px;
        overflow-y: auto;
        box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.5);
    }}
    
    .log-entry {{
        margin-bottom: 8px;
        padding: 5px 0;
        border-bottom: 1px solid #111;
        line-height: 1.6;
    }}
    
    .log-timestamp {{
        color: {COLORS['text_secondary']};
        font-size: 0.85em;
    }}
    
    .log-level-info {{
        color: {COLORS['accent_primary']};
    }}
    
    .log-level-success {{
        color: {COLORS['accent_success']};
    }}
    
    .log-level-warning {{
        color: {COLORS['accent_warning']};
    }}
    
    .log-level-error {{
        color: {COLORS['accent_error']};
    }}
    
    .log-cursor {{
        color: {COLORS['accent_success']};
        animation: blink 1s step-end infinite;
    }}
    
    /* ===== ANIMATIONS ===== */
    @keyframes pulse {{
        0%, 100% {{
            opacity: 1;
        }}
        50% {{
            opacity: 0.5;
        }}
    }}
    
    @keyframes pulse-glow {{
        0%, 100% {{
            box-shadow: 0 4px 15px {COLORS['glow']};
        }}
        50% {{
            box-shadow: 0 4px 25px {COLORS['glow']};
        }}
    }}
    
    @keyframes blink {{
        0%, 50% {{
            opacity: 1;
        }}
        51%, 100% {{
            opacity: 0;
        }}
    }}
    
    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes slideIn {{
        from {{
            transform: translateX(-20px);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.5s ease-out;
    }}
    
    .slide-in {{
        animation: slideIn 0.5s ease-out;
    }}
    
    /* ===== FORMS ===== */
    .stTextArea textarea {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid {COLORS['border']} !important;
        border-radius: 12px !important;
        color: {COLORS['text_primary']} !important;
        font-family: 'Inter', sans-serif !important;
        padding: 15px !important;
    }}
    
    .stTextArea textarea:focus {{
        border-color: {COLORS['accent_primary']} !important;
        box-shadow: 0 0 15px {COLORS['glow']} !important;
    }}
    
    .stButton button {{
        background: linear-gradient(135deg, {COLORS['accent_primary']}, {COLORS['accent_secondary']}) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 30px !important;
        font-weight: 600 !important;
        font-size: 1em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px {COLORS['glow']} !important;
    }}
    
    .stButton button:hover {{
        box-shadow: 0 6px 25px {COLORS['glow']} !important;
        transform: translateY(-2px) !important;
    }}
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {COLORS['bg_secondary']};
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['accent_primary']};
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['accent_secondary']};
    }}
    
    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {{
        .nexus-header {{
            flex-direction: column;
            gap: 15px;
        }}
        
        .pipeline {{
            flex-direction: column;
        }}
        
        .pipeline-arrow {{
            transform: rotate(90deg);
            margin: 10px 0;
        }}
        
        .council-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    </style>
    """
