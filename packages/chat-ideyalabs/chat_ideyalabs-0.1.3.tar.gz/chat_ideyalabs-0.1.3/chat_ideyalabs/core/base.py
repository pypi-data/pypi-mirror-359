"""
Base classes for chat messages, similar to langchain structure
"""

from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class BaseMessage(ABC):
    """Base class for all message types."""
    
    def __init__(self, content: str, **kwargs):
        self.content = content
        self.additional_kwargs = kwargs
    
    @property
    @abstractmethod
    def type(self) -> str:
        """Return the message type."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        return {
            "role": self.type,
            "content": self.content,
            **self.additional_kwargs
        }


class HumanMessage(BaseMessage):
    """Human message class."""
    
    @property
    def type(self) -> str:
        return "user"


class AIMessage(BaseMessage):
    """AI assistant message class."""
    
    @property
    def type(self) -> str:
        return "assistant"


class SystemMessage(BaseMessage):
    """System message class."""
    
    @property
    def type(self) -> str:
        return "system"


def messages_to_dict(messages: List[BaseMessage]) -> List[Dict[str, Any]]:
    """Convert list of messages to dictionary format for API calls."""
    return [message.to_dict() for message in messages] 