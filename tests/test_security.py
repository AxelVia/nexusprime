"""Tests for security utilities."""

from __future__ import annotations

import os
import pytest

from nexusprime.utils.security import get_required_env, validate_generated_code


class TestGetRequiredEnv:
    """Test cases for get_required_env."""
    
    def test_get_existing_env_var(self, monkeypatch):
        """Test retrieving an existing environment variable."""
        monkeypatch.setenv("TEST_VAR", "test_value")
        assert get_required_env("TEST_VAR") == "test_value"
    
    def test_get_missing_env_var(self, monkeypatch):
        """Test that missing env var raises EnvironmentError."""
        monkeypatch.delenv("TEST_VAR", raising=False)
        
        with pytest.raises(EnvironmentError) as exc_info:
            get_required_env("TEST_VAR")
        
        assert "TEST_VAR" in str(exc_info.value)
    
    def test_get_empty_env_var(self, monkeypatch):
        """Test that empty env var raises EnvironmentError."""
        monkeypatch.setenv("TEST_VAR", "")
        
        with pytest.raises(EnvironmentError):
            get_required_env("TEST_VAR")


class TestValidateGeneratedCode:
    """Test cases for validate_generated_code."""
    
    def test_safe_code(self):
        """Test validation of safe code."""
        code = """
def add(a, b):
    return a + b

print(add(1, 2))
"""
        is_safe, warnings = validate_generated_code(code)
        assert is_safe is True
        assert len(warnings) == 0
    
    def test_os_system(self):
        """Test detection of os.system."""
        code = "import os\nos.system('ls')"
        is_safe, warnings = validate_generated_code(code)
        assert is_safe is False
        assert any("os.system" in w for w in warnings)
    
    def test_subprocess(self):
        """Test detection of subprocess."""
        code = "import subprocess\nsubprocess.run(['ls'])"
        is_safe, warnings = validate_generated_code(code)
        assert is_safe is False
        assert any("subprocess" in w for w in warnings)
    
    def test_eval(self):
        """Test detection of eval."""
        code = "result = eval('1 + 1')"
        is_safe, warnings = validate_generated_code(code)
        assert is_safe is False
        assert any("eval" in w for w in warnings)
    
    def test_exec(self):
        """Test detection of exec."""
        code = "exec('print(\"hello\")')"
        is_safe, warnings = validate_generated_code(code)
        assert is_safe is False
        assert any("exec" in w for w in warnings)
    
    def test_multiple_issues(self):
        """Test detection of multiple security issues."""
        code = """
import os
import subprocess

os.system('ls')
subprocess.run(['pwd'])
eval('1 + 1')
"""
        is_safe, warnings = validate_generated_code(code)
        assert is_safe is False
        assert len(warnings) >= 3
    
    def test_file_writing(self):
        """Test detection of file writing."""
        code = "with open('file.txt', 'w') as f: f.write('test')"
        is_safe, warnings = validate_generated_code(code)
        assert is_safe is False
        assert any("write mode" in w for w in warnings)
