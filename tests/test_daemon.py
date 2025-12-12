"""Tests for nexus_daemon module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestLoadRequest:
    """Test load_request function."""
    
    def test_load_request_valid(self, tmp_path):
        """Test loading a valid request."""
        # Import inside test to avoid side effects
        from nexus_daemon import load_request
        
        request_file = tmp_path / "request.json"
        request_data = {
            "prompt": "Test prompt",
            "env_mode": "DEV",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        with open(request_file, "w") as f:
            json.dump(request_data, f)
        
        with patch("nexus_daemon.REQUEST_FILE", str(request_file)):
            result = load_request()
        
        assert result is not None
        assert result["prompt"] == "Test prompt"
        assert result["env_mode"] == "DEV"
    
    def test_load_request_nonexistent(self, tmp_path):
        """Test loading when file doesn't exist."""
        from nexus_daemon import load_request
        
        request_file = tmp_path / "nonexistent.json"
        
        with patch("nexus_daemon.REQUEST_FILE", str(request_file)):
            result = load_request()
        
        assert result is None
    
    def test_load_request_invalid_json(self, tmp_path):
        """Test loading invalid JSON."""
        from nexus_daemon import load_request
        
        request_file = tmp_path / "request.json"
        
        with open(request_file, "w") as f:
            f.write("invalid json {")
        
        with patch("nexus_daemon.REQUEST_FILE", str(request_file)):
            result = load_request()
        
        assert result is None


class TestArchiveRequest:
    """Test archive_request function."""
    
    def test_archive_request(self, tmp_path):
        """Test archiving a request."""
        from nexus_daemon import archive_request
        
        request_file = tmp_path / "request.json"
        processed_file = tmp_path / "request.processed.json"
        
        # Create request file
        request_data = {
            "prompt": "Test prompt",
            "env_mode": "DEV",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        with open(request_file, "w") as f:
            json.dump(request_data, f)
        
        # Archive it
        with patch("nexus_daemon.REQUEST_FILE", str(request_file)), \
             patch("nexus_daemon.PROCESSED_FILE", str(processed_file)):
            archive_request(request_data)
        
        # Check original is removed
        assert not request_file.exists()
        
        # Check processed file exists and contains data
        assert processed_file.exists()
        with open(processed_file) as f:
            processed_data = json.load(f)
        
        assert processed_data["prompt"] == "Test prompt"
        assert processed_data["env_mode"] == "DEV"
        assert "processed_at" in processed_data


class TestInitializeStatus:
    """Test initialize_status function."""
    
    def test_initialize_status(self, tmp_path):
        """Test status initialization."""
        from nexus_daemon import initialize_status
        
        status_file = tmp_path / "status.json"
        
        with patch("nexus_daemon.STATUS_FILE", str(status_file)):
            initialize_status("Test prompt", "PROD")
        
        assert status_file.exists()
        
        with open(status_file) as f:
            status_data = json.load(f)
        
        assert status_data["current_status"] == "INITIALIZING"
        assert status_data["env_mode"] == "PROD"
        assert status_data["quality_score"] == 0
        assert status_data["feedback_loop_count"] == 0
        assert "Test prompt" in status_data["spec_excerpt"]
