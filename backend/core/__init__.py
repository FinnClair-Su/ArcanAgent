"""
ArcanAgent Core Systems

This package contains the core engines and systems that power ArcanAgent:
- Tool Call Engine: Handles recursive tool calling inspired by NagaAgent
- Context Manager: Implements the 6 context engineering principles
- Bidirectional Links Engine: The heart of our knowledge management system
- LLM Client: Unified interface for different LLM providers
"""

from .bidirectional_links import BidirectionalLinkEngine
from .context_manager import ContextManager
from .tool_call_engine import ToolCallEngine
from .llm_client import LLMClient, get_llm_client

__all__ = [
    "BidirectionalLinkEngine",
    "ContextManager", 
    "ToolCallEngine",
    "LLMClient",
    "get_llm_client"
]