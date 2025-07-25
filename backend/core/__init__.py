"""
ArcanAgent Core Systems

This package contains the core engines and systems that power ArcanAgent:
- Tool Call Engine: Handles recursive tool calling inspired by NagaAgent
- Context Manager: Implements the 6 context engineering principles
- Bidirectional Links Engine: The heart of our knowledge management system
- LLM Client: Unified interface for different LLM providers
"""

from .bidirectional_links import BidirectionalLinkEngine, LinkAnalysis, PathInfo
from .llm_client import (
    BaseLLMClient, 
    LLMMessage, 
    LLMResponse, 
    LLMConfig,
    LLMProvider,
    get_llm_client,
    get_llm_client_manager,
    chat_completion
)
from .llm_initializer import initialize_llm_clients, get_provider_status, test_llm_client
from .context_manager import ContextManager, ContextItem, ContextWindow, ContextType, ContextPriority
from .tool_call_engine import (
    ToolCallEngine, 
    BaseTool, 
    ToolCall, 
    ToolDefinition,
    ToolCallStatus,
    SearchKnowledgeTool,
    AnalyzeLinksTool
)

__all__ = [
    "BidirectionalLinkEngine",
    "LinkAnalysis",
    "PathInfo",
    "BaseLLMClient",
    "LLMMessage",
    "LLMResponse", 
    "LLMConfig",
    "LLMProvider",
    "get_llm_client",
    "get_llm_client_manager",
    "chat_completion",
    "initialize_llm_clients",
    "get_provider_status",
    "test_llm_client",
    "ContextManager",
    "ContextItem", 
    "ContextWindow",
    "ContextType",
    "ContextPriority",
    "ToolCallEngine",
    "BaseTool",
    "ToolCall", 
    "ToolDefinition",
    "ToolCallStatus",
    "SearchKnowledgeTool",
    "AnalyzeLinksTool",
]