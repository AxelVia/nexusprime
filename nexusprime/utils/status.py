"""Status file management utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

from .logging import get_logger

if TYPE_CHECKING:
    from ..core.state import NexusFactoryState

logger = get_logger(__name__)


def save_status_snapshot(state: Dict[str, Any], status_file: str = "status.json") -> None:
    """
    Export current state to JSON file for dashboard consumption.
    
    Args:
        state: Current factory state
        status_file: Path to status file
    """
    try:
        snapshot = {
            "current_status": state.get("current_status"),
            "env_mode": state.get("env_mode"),
            "quality_score": state.get("quality_score"),
            "feedback_loop_count": state.get("feedback_loop_count"),
            "spec_excerpt": state.get("spec_document", "")[:200],
            "last_message": state["messages"][-1].content if state.get("messages") else "",
            "total_tokens": state.get("total_tokens", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
        }
        
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
        
        logger.debug(f"Status snapshot saved to {status_file}")
    except (OSError, IOError) as e:
        logger.error(f"Failed to save status snapshot: {e}")
    except Exception as e:
        logger.error(f"Unexpected error saving status snapshot: {e}")


def load_status_snapshot(status_file: str = "status.json") -> Optional[Dict[str, Any]]:
    """
    Load status snapshot from JSON file.
    
    Args:
        status_file: Path to status file
    
    Returns:
        Status dictionary or None if file doesn't exist or is invalid
    """
    try:
        status_path = Path(status_file)
        if not status_path.exists():
            logger.debug(f"Status file {status_file} does not exist")
            return None
        
        with open(status_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in status file {status_file}: {e}")
        return None
    except (OSError, IOError) as e:
        logger.error(f"Failed to load status file {status_file}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading status file: {e}")
        return None
