"""
Chat Ideyalabs - A langchain-like wrapper for Ideyalabs LLM API
"""

from .core.chat_ideyalabs import ChatIdeyalabs
from .core.base import BaseMessage, HumanMessage, AIMessage, SystemMessage

__version__ = "0.1.5"
__all__ = ["ChatIdeyalabs", "BaseMessage", "HumanMessage", "AIMessage", "SystemMessage"] 