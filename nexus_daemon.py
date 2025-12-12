#!/usr/bin/env python3
"""
NexusPrime Daemon
=================

Monitors request.json file and launches the factory when a new request is detected.
This daemon polls the request file every 2-3 seconds and processes incoming requests.
"""

from __future__ import annotations

import json
import time
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

from nexusprime import build_nexus_factory
from nexusprime.utils.logging import get_logger
from nexusprime.utils.status import save_status_snapshot

logger = get_logger(__name__)

# Configuration
REQUEST_FILE = "request.json"
PROCESSED_FILE = "request.processed.json"
STATUS_FILE = "status.json"
POLL_INTERVAL = 2.5  # seconds


def load_request() -> Optional[Dict[str, Any]]:
    """
    Load request from request.json file.
    
    Returns:
        Request dictionary or None if file doesn't exist or is invalid
    """
    try:
        request_path = Path(REQUEST_FILE)
        if not request_path.exists():
            return None
        
        with open(REQUEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {REQUEST_FILE}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading {REQUEST_FILE}: {e}")
        return None


def archive_request(request_data: Dict[str, Any]) -> None:
    """
    Archive the processed request by renaming the file.
    
    Args:
        request_data: Request data to archive
    """
    try:
        # Save to processed file for history
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            json.dump({
                **request_data,
                "processed_at": datetime.now().isoformat()
            }, f, indent=2)
        
        # Remove original request file
        if Path(REQUEST_FILE).exists():
            os.remove(REQUEST_FILE)
            logger.info(f"Archived request to {PROCESSED_FILE}")
    except Exception as e:
        logger.error(f"Error archiving request: {e}")


def initialize_status(prompt: str, env_mode: str) -> None:
    """
    Initialize status.json with initial state.
    
    Args:
        prompt: User prompt
        env_mode: Environment mode (DEV or PROD)
    """
    try:
        # Truncate prompt for excerpt if needed
        prompt_excerpt = prompt[:200]
        if len(prompt) > 200:
            prompt_excerpt += "..."
        
        initial_status = {
            "current_status": "INITIALIZING",
            "env_mode": env_mode,
            "quality_score": 0,
            "feedback_loop_count": 0,
            "spec_excerpt": f"Request: {prompt_excerpt}",
            "last_message": "Factory starting...",
            "total_tokens": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_status, f, indent=2)
        
        logger.info("Status initialized")
    except Exception as e:
        logger.error(f"Error initializing status: {e}")


def process_request(request_data: Dict[str, Any]) -> None:
    """
    Process a request by running the factory.
    
    Args:
        request_data: Request data containing prompt and env_mode
    """
    prompt = request_data.get("prompt", "")
    env_mode = request_data.get("env_mode", "DEV")
    timestamp = request_data.get("timestamp", "")
    
    logger.info(f"Processing request from {timestamp}")
    logger.info(f"Prompt: {prompt[:100]}...")
    logger.info(f"Environment: {env_mode}")
    
    try:
        # Initialize status for dashboard
        initialize_status(prompt, env_mode)
        
        # Build the factory
        logger.info("Building NexusPrime factory...")
        app = build_nexus_factory()
        
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=prompt)],
            "env_mode": env_mode,
            "feedback_loop_count": 0
        }
        
        # Run the factory
        logger.info("Starting factory execution...")
        final_state = app.invoke(initial_state)
        
        # Save final status
        save_status_snapshot(final_state, STATUS_FILE)
        
        logger.info("Factory execution completed")
        logger.info(f"Final Status: {final_state.get('current_status')}")
        logger.info(f"Quality Score: {final_state.get('quality_score')}")
        logger.info(f"Environment: {final_state.get('env_mode')}")
        
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        
        # Update status with error
        try:
            error_status = {
                "current_status": "ERROR",
                "env_mode": env_mode,
                "quality_score": 0,
                "feedback_loop_count": 0,
                "spec_excerpt": f"Request: {prompt[:200]}...",
                "last_message": f"Error: {str(e)}",
                "total_tokens": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(error_status, f, indent=2)
        except Exception as status_error:
            logger.error(f"Error updating status with error: {status_error}")


def run_daemon() -> None:
    """
    Main daemon loop that monitors request.json and processes requests.
    """
    logger.info("=" * 60)
    logger.info("NexusPrime Daemon Started")
    logger.info("=" * 60)
    logger.info(f"Monitoring: {REQUEST_FILE}")
    logger.info(f"Poll interval: {POLL_INTERVAL}s")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    try:
        while True:
            # Check for new request
            request_data = load_request()
            
            if request_data:
                logger.info("New request detected!")
                
                # Archive the request immediately to prevent reprocessing
                archive_request(request_data)
                
                # Process the request
                process_request(request_data)
                
                logger.info("Request processing completed")
                logger.info("-" * 60)
            
            # Wait before next poll
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("NexusPrime Daemon Stopped")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Fatal error in daemon: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_daemon()
