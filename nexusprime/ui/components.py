"""Reusable UI components for NexusPrime dashboard."""

from typing import Dict, List, Optional, Tuple
from datetime import datetime


def render_header(user_name: str = "ADMIN", plan: str = "PRO") -> str:
    """
    Render the premium header with gradient logo and status indicator.
    
    Args:
        user_name: User name to display
        plan: Plan type (PRO, FREE, etc.)
    
    Returns:
        HTML string for header
    """
    return f"""
    <div class="nexus-header fade-in">
        <div>
            <div class="brand-logo">
                🔮 NEXUSPRIME
                <span class="brand-subtitle">// AI SOFTWARE FACTORY</span>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <span class="multi-llm-badge">Multi-LLM ✨</span>
            <div class="status-indicator">
                <div class="status-dot"></div>
                <span>Online</span>
            </div>
            <div style="background: rgba(255, 255, 255, 0.05); padding: 8px 16px; border-radius: 20px; font-size: 0.85em;">
                @{user_name} | {plan}
            </div>
        </div>
    </div>
    """


def render_metrics_card(
    label: str,
    value: str,
    icon: str = "📊",
    progress: Optional[int] = None,
    color: str = "#6366f1"
) -> str:
    """
    Render a metric card with optional progress bar.
    
    Args:
        label: Metric label
        value: Metric value to display
        icon: Icon emoji
        progress: Optional progress percentage (0-100)
        color: Color for the accent
    
    Returns:
        HTML string for metric card
    """
    progress_bar = ""
    if progress is not None:
        # Cap progress at 100%
        progress = min(100, max(0, progress))
        progress_bar = f"""
        <div class="metric-progress">
            <div class="metric-progress-bar" style="width: {progress}%; background: {color};"></div>
        </div>
        """
    
    return f"""
    <div class="nexus-card metric-container">
        <div class="card-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        {progress_bar}
    </div>
    """


def render_progress_pipeline(current_step: str) -> str:
    """
    Render the horizontal progress pipeline.
    
    Args:
        current_step: Current active step name
    
    Returns:
        HTML string for pipeline
    """
    steps = [
        ("Input", "📥", "input"),
        ("Product Owner", "🕵️", "po"),
        ("Tech Lead", "🌐", "tech"),
        ("Dev Squad", "⚡", "dev"),
        ("Council", "⚖️", "council"),
        ("Output", "✅", "output"),
    ]
    
    # Determine step status
    step_order = {s[2]: i for i, s in enumerate(steps)}
    current_idx = step_order.get(current_step.lower(), -1)
    
    pipeline_html = ['<div class="pipeline">']
    
    for idx, (label, icon, step_key) in enumerate(steps):
        # Determine CSS class
        if idx < current_idx:
            css_class = "completed"
        elif idx == current_idx:
            css_class = "active"
        else:
            css_class = "pending"
        
        pipeline_html.append(f"""
        <div class="pipeline-step {css_class}">
            <div class="pipeline-icon">{icon}</div>
            <div class="pipeline-label">{label}</div>
        </div>
        """)
        
        # Add arrow between steps
        if idx < len(steps) - 1:
            pipeline_html.append('<span class="pipeline-arrow">→</span>')
    
    pipeline_html.append('</div>')
    
    return ''.join(pipeline_html)


def render_active_agent(
    agent_name: str,
    model: str,
    status: str,
    progress: int = 0
) -> str:
    """
    Render the active agent card with real-time status.
    
    Args:
        agent_name: Name of the active agent
        model: LLM model being used
        status: Current status message
        progress: Progress percentage (0-100)
    
    Returns:
        HTML string for active agent card
    """
    # Map agent to icon
    agent_icons = {
        "Product Owner": "🕵️",
        "Tech Lead": "🌐",
        "Dev Squad": "⚡",
        "Council": "⚖️",
    }
    icon = agent_icons.get(agent_name, "🤖")
    
    return f"""
    <div class="nexus-card agent-card fade-in">
        <div class="card-title">
            <span class="card-icon">🎯</span>
            ACTIVE AGENT
        </div>
        <div class="agent-header">
            <div class="agent-name">
                <span>{icon}</span>
                <span>{agent_name.upper()}</span>
            </div>
            <div class="agent-model">
                Powered by {model}
            </div>
        </div>
        <div class="agent-status">{status}</div>
        <div class="metric-progress">
            <div class="metric-progress-bar" style="width: {progress}%;"></div>
        </div>
        <div style="text-align: right; font-size: 0.9em; color: #94a3b8; margin-top: 10px;">
            {progress}% Complete
        </div>
    </div>
    """


def render_council_section(
    judges: Optional[List[Dict[str, any]]] = None,
    arbitrator: Optional[Dict[str, any]] = None,
    previous_score: Optional[int] = None
) -> str:
    """
    Render the council review section with 3 judges + arbitrator.
    
    Args:
        judges: List of judge dicts with keys: name, model, score, verdict, concerns
        arbitrator: Arbitrator dict with keys: score, reasoning, verdict
        previous_score: Previous review score for comparison
    
    Returns:
        HTML string for council section
    """
    if not judges:
        # Default placeholder
        judges = [
            {"name": "Grok", "model": "grok-3", "score": "--", "verdict": "PENDING"},
            {"name": "Gemini", "model": "gemini-2.5-pro", "score": "--", "verdict": "PENDING"},
            {"name": "Claude", "model": "claude-sonnet-4", "score": "--", "verdict": "PENDING"},
        ]
    
    council_html = ["""
    <div class="nexus-card">
        <div class="card-title">
            <span class="card-icon">⚖️</span>
            COUNCIL REVIEW (Multi-LLM Debate)
        </div>
        <div class="council-grid">
    """]
    
    # Render judge cards
    for judge in judges:
        score_display = judge.get("score", "--")
        score_color = "#6366f1"
        
        if isinstance(score_display, (int, float)):
            if score_display >= 80:
                score_color = "#10b981"
            elif score_display >= 60:
                score_color = "#f59e0b"
            else:
                score_color = "#ef4444"
        
        verdict = judge.get("verdict", "PENDING")
        verdict_class = "verdict-pending"
        if verdict == "APPROVE":
            verdict_class = "verdict-approve"
        elif verdict == "REJECT":
            verdict_class = "verdict-reject"
        
        judge_icon = {"Grok": "🔸", "Gemini": "🔹", "Claude": "🔷"}.get(judge["name"], "⚪")
        
        council_html.append(f"""
        <div class="judge-card slide-in">
            <div style="font-size: 2em; margin-bottom: 10px;">{judge_icon}</div>
            <div class="judge-name">{judge["name"]}</div>
            <div class="judge-model">{judge.get("model", "")}</div>
            <div class="score-circle" style="border-color: {score_color}; color: {score_color};">
                {score_display}
            </div>
            <div style="font-size: 0.7em; color: #94a3b8; margin-bottom: 10px;">
                /100
            </div>
            <span class="verdict-badge {verdict_class}">{verdict}</span>
        </div>
        """)
    
    council_html.append('</div>')
    
    # Arbitrator section
    if arbitrator:
        arb_score = arbitrator.get("score", "--")
        arb_reasoning = arbitrator.get("reasoning", "Pending arbitration...")
        arb_verdict = arbitrator.get("verdict", "PENDING")
        
        verdict_class = "verdict-pending"
        if arb_verdict == "APPROVE":
            verdict_class = "verdict-approve"
        elif arb_verdict == "REJECT":
            verdict_class = "verdict-reject"
        
        # Add progression indicator if available
        progression_html = ""
        if previous_score is not None and isinstance(arb_score, (int, float)):
            score_change = arb_score - previous_score
            change_icon = "📈" if score_change > 0 else "📉" if score_change < 0 else "➡️"
            change_color = "#10b981" if score_change > 0 else "#ef4444" if score_change < 0 else "#94a3b8"
            progression_html = f"""
            <div style="margin-top: 15px; padding: 10px; background: rgba(255, 255, 255, 0.05); 
                        border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);">
                <div style="font-size: 0.9em; color: #94a3b8; margin-bottom: 5px;">
                    📈 Progression vs Previous Review:
                </div>
                <div style="font-size: 1.2em; font-weight: 600; color: {change_color};">
                    {change_icon} {score_change:+d} points ({previous_score} → {arb_score})
                </div>
            </div>
            """
        
        council_html.append(f"""
        <div class="arbitrator-card fade-in" style="margin-top: 20px;">
            <div style="font-size: 1.2em; font-weight: 600; margin-bottom: 15px;">
                ⚖️ FINAL ARBITRATION (Claude)
            </div>
            <div style="font-size: 2.5em; font-weight: 800; color: #6366f1; margin: 20px 0;">
                {arb_score}/100
            </div>
            <span class="verdict-badge {verdict_class}" style="font-size: 1em; padding: 8px 20px;">
                {arb_verdict}
            </span>
            <div style="margin-top: 20px; font-size: 0.9em; color: #94a3b8; line-height: 1.6;">
                {arb_reasoning}
            </div>
            {progression_html}
        </div>
        """)
    else:
        council_html.append("""
        <div class="arbitrator-card" style="margin-top: 20px;">
            <div style="font-size: 1.2em; font-weight: 600; margin-bottom: 15px;">
                ⚖️ FINAL ARBITRATION
            </div>
            <div style="font-size: 1.5em; color: #f59e0b; margin: 20px 0;">
                Awaiting reviews...
            </div>
        </div>
        """)
    
    # Add concerns summary if available
    if judges:
        all_concerns = []
        for judge in judges:
            concerns = judge.get("concerns", [])
            if concerns:
                for concern in concerns:
                    if concern and concern not in all_concerns:
                        all_concerns.append((judge["name"], concern))
        
        if all_concerns:
            council_html.append("""
            <div style="margin-top: 20px; padding: 20px; background: rgba(239, 68, 68, 0.1); 
                        border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.3);">
                <div style="font-size: 1.1em; font-weight: 600; margin-bottom: 15px; color: #ef4444;">
                    📝 Concerns Identifiées:
                </div>
            """)
            
            for judge_name, concern in all_concerns:
                council_html.append(f"""
                <div style="margin: 8px 0; padding: 8px 12px; background: rgba(0, 0, 0, 0.2); 
                            border-radius: 6px; border-left: 3px solid #ef4444;">
                    <span style="color: #94a3b8; font-size: 0.85em;">{judge_name}:</span>
                    <span style="color: #f8fafc; margin-left: 8px;">{concern}</span>
                </div>
                """)
            
            council_html.append('</div>')
    
    council_html.append('</div>')
    
    return ''.join(council_html)


def render_terminal(
    logs: List[Tuple[str, str, str]],
    max_lines: int = 20
) -> str:
    """
    Render terminal/console with logs.
    
    Args:
        logs: List of tuples (timestamp, level, message)
        max_lines: Maximum number of log lines to display
    
    Returns:
        HTML string for terminal
    """
    terminal_html = ['<div class="terminal-container">']
    
    if not logs:
        terminal_html.append("""
        <div class="log-entry">
            <span class="log-timestamp">[--:--:--]</span>
            <span class="log-level-info"> SYSTEM:</span> 
            Waiting for factory to start...
        </div>
        """)
    else:
        # Show last N logs
        recent_logs = logs[-max_lines:] if len(logs) > max_lines else logs
        
        for timestamp, level, message in recent_logs:
            level_class = f"log-level-{level.lower()}"
            terminal_html.append(f"""
            <div class="log-entry">
                <span class="log-timestamp">[{timestamp}]</span>
                <span class="{level_class}"> {level.upper()}:</span> 
                {message}
            </div>
            """)
    
    # Add blinking cursor
    terminal_html.append('<div class="log-cursor">█</div>')
    terminal_html.append('</div>')
    
    return ''.join(terminal_html)


def render_workspace_files(workspace_path: str = "workspace") -> str:
    """
    Render workspace file list.
    
    Args:
        workspace_path: Path to workspace directory
    
    Returns:
        HTML string for file list
    """
    import os
    
    file_html = ["""
    <div class="nexus-card">
        <div class="card-title">
            <span class="card-icon">📂</span>
            WORKSPACE FILES
        </div>
    """]
    
    if os.path.exists(workspace_path):
        try:
            files = os.listdir(workspace_path)
            if files:
                for fname in sorted(files):
                    file_icon = "📄" if "." in fname else "📁"
                    file_html.append(f"""
                    <div style="padding: 8px; border-bottom: 1px solid #2d2d3a; font-family: monospace; font-size: 0.9em;">
                        {file_icon} {fname}
                    </div>
                    """)
            else:
                file_html.append('<div style="color: #94a3b8; padding: 20px; text-align: center;">No files yet</div>')
        except Exception as e:
            file_html.append(f'<div style="color: #ef4444; padding: 20px;">Error: {e}</div>')
    else:
        file_html.append('<div style="color: #94a3b8; padding: 20px; text-align: center;">Workspace not found</div>')
    
    file_html.append('</div>')
    
    return ''.join(file_html)
