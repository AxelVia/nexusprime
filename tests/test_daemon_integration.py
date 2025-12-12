"""Integration test for the complete daemon workflow."""

import json
import time
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


def test_daemon_workflow_integration(tmp_path):
    """Test the complete daemon workflow with a mock request."""
    # Setup temporary directory for files
    request_file = tmp_path / "request.json"
    processed_file = tmp_path / "request.processed.json"
    status_file = tmp_path / "status.json"
    
    # Create a test request
    request_data = {
        "prompt": "Create a simple Python calculator",
        "env_mode": "DEV",
        "timestamp": "2024-01-01T00:00:00"
    }
    
    with open(request_file, "w") as f:
        json.dump(request_data, f)
    
    # Import daemon functions with patched paths
    with patch("nexus_daemon.REQUEST_FILE", str(request_file)), \
         patch("nexus_daemon.PROCESSED_FILE", str(processed_file)), \
         patch("nexus_daemon.STATUS_FILE", str(status_file)):
        
        from nexus_daemon import load_request, archive_request, initialize_status
        
        # Step 1: Load request
        loaded = load_request()
        assert loaded is not None
        assert loaded["prompt"] == "Create a simple Python calculator"
        assert loaded["env_mode"] == "DEV"
        
        # Step 2: Initialize status
        initialize_status(loaded["prompt"], loaded["env_mode"])
        assert status_file.exists()
        
        with open(status_file) as f:
            status = json.load(f)
        
        assert status["current_status"] == "INITIALIZING"
        assert status["env_mode"] == "DEV"
        assert "calculator" in status["spec_excerpt"]
        
        # Step 3: Archive request
        archive_request(loaded)
        assert not request_file.exists()
        assert processed_file.exists()
        
        with open(processed_file) as f:
            processed = json.load(f)
        
        assert processed["prompt"] == "Create a simple Python calculator"
        assert "processed_at" in processed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
