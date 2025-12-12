"""Security utilities for NexusPrime."""

from __future__ import annotations

import os
import re
from typing import List, Tuple

from .logging import get_logger

logger = get_logger(__name__)


def get_required_env(key: str) -> str:
    """
    Retrieve a required environment variable.
    
    Args:
        key: Environment variable name
    
    Returns:
        Environment variable value
    
    Raises:
        EnvironmentError: If the environment variable is not set
    """
    value = os.getenv(key)
    if value is None or value == "":
        error_msg = f"Required environment variable '{key}' is not set"
        logger.error(error_msg)
        raise EnvironmentError(error_msg)
    return value


def validate_generated_code(code: str) -> Tuple[bool, List[str]]:
    """
    Validate generated Python code for potentially dangerous imports and patterns.
    
    Args:
        code: Python code to validate
    
    Returns:
        Tuple of (is_safe, list_of_warnings)
        - is_safe: True if no dangerous patterns found, False otherwise
        - list_of_warnings: List of warning messages about dangerous patterns
    """
    warnings: List[str] = []
    
    # Dangerous imports to check
    dangerous_patterns = [
        (r'\bos\.system\b', "os.system() - Command execution"),
        (r'\bsubprocess\.', "subprocess module - Process execution"),
        (r'\beval\s*\(', "eval() - Code evaluation"),
        (r'\bexec\s*\(', "exec() - Code execution"),
        (r'\b__import__\s*\(', "__import__() - Dynamic imports"),
        (r'\bcompile\s*\(', "compile() - Code compilation"),
        (r'\bopen\s*\([^)]*[\'"][wWaA]', "open() with write/append mode - File writing"),
        (r'\bshutil\.rmtree\b', "shutil.rmtree() - Recursive deletion"),
        (r'\bos\.remove\b', "os.remove() - File deletion"),
        (r'\bos\.unlink\b', "os.unlink() - File deletion"),
    ]
    
    for pattern, description in dangerous_patterns:
        if re.search(pattern, code):
            warning_msg = f"Potentially dangerous code detected: {description}"
            warnings.append(warning_msg)
            logger.warning(warning_msg)
    
    is_safe = len(warnings) == 0
    
    if not is_safe:
        logger.warning(f"Code validation found {len(warnings)} potential security issues")
    
    return is_safe, warnings
