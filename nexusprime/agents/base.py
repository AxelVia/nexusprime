"""Base agent class for NexusPrime agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any

from ..core.state import NexusFactoryState
from ..utils.logging import get_logger


class Agent(ABC):
    """Abstract base class for all NexusPrime agents."""
    
    def __init__(self):
        """Initialize agent."""
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def execute(self, state: NexusFactoryState) -> Dict[str, Any]:
        """
        Execute agent logic.
        
        Args:
            state: Current factory state
        
        Returns:
            State updates to apply
        """
        pass
    
    def log_execution(self, message: str) -> None:
        """
        Log agent execution message.
        
        Args:
            message: Message to log
        """
        self.logger.info(f"[{self.__class__.__name__}] {message}")
