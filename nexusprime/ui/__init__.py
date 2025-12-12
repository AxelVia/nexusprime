"""UI module for NexusPrime dashboard components."""

from .styles import COLORS, get_base_styles
from .components import (
    render_header,
    render_metrics_card,
    render_progress_pipeline,
    render_active_agent,
    render_council_section,
    render_terminal,
)

__all__ = [
    "COLORS",
    "get_base_styles",
    "render_header",
    "render_metrics_card",
    "render_progress_pipeline",
    "render_active_agent",
    "render_council_section",
    "render_terminal",
]
