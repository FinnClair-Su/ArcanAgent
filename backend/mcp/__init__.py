"""
MCP (Model Context Protocol) Module
Core infrastructure for Agent communication
"""

from .protocol import MCPMessage, MCPRequest, MCPResponse
from .server import MCPServer
from .client import MCPClient
from .router import MCPRouter
from .capabilities import CapabilityRegistry
from .middleware import MCPMiddleware

__all__ = [
    "MCPMessage",
    "MCPRequest", 
    "MCPResponse",
    "MCPServer",
    "MCPClient",
    "MCPRouter",
    "CapabilityRegistry",
    "MCPMiddleware",
]