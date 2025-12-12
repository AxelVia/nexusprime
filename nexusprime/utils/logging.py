"""Structured logging configuration for NexusPrime."""

from __future__ import annotations

import logging
import sys
from typing import Optional


def get_logger(name: str, log_file: str = "nexus.log", level: int = logging.INFO) -> logging.Logger:
    """
    Get or create a configured logger for NexusPrime.
    
    Args:
        name: Logger name (typically __name__ of the module)
        log_file: Path to log file
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (OSError, IOError) as e:
        logger.warning(f"Could not create file handler for {log_file}: {e}")
    
    return logger
