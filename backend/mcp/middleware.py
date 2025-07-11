"""
MCP Middleware
Authentication, logging, and rate limiting for MCP messages
"""

import logging
import time
from typing import Dict, Any, Optional
from collections import defaultdict, deque

from .protocol import MCPMessage, MCPRequest, MCPResponse


logger = logging.getLogger(__name__)


class MCPMiddleware:
    """MCP middleware for message processing"""
    
    def __init__(self):
        self.rate_limits: Dict[str, deque] = defaultdict(deque)
        self.rate_limit_window = 60  # 1 minute window
        self.rate_limit_max = 100    # 100 requests per minute
        self.authenticated_agents: Dict[str, Dict[str, Any]] = {}
    
    async def process_incoming(self, message: MCPMessage) -> MCPMessage:
        """Process incoming message"""
        # Log message
        await self._log_message(message, "incoming")
        
        # Check rate limits
        if not await self._check_rate_limit(message.source_agent):
            raise RuntimeError(f"Rate limit exceeded for agent: {message.source_agent}")
        
        # Authenticate if needed
        if isinstance(message, MCPRequest):
            if not await self._authenticate_request(message):
                raise RuntimeError(f"Authentication failed for agent: {message.source_agent}")
        
        # Add timing information
        message.metadata["middleware_start"] = time.time()
        
        return message
    
    async def process_outgoing(self, message: MCPMessage) -> MCPMessage:
        """Process outgoing message"""
        # Log message
        await self._log_message(message, "outgoing")
        
        # Add timing information
        if "middleware_start" in message.metadata:
            processing_time = time.time() - message.metadata["middleware_start"]
            message.metadata["processing_time"] = processing_time
        
        return message
    
    async def _log_message(self, message: MCPMessage, direction: str):
        """Log message"""
        logger.info(
            f"MCP {direction}: {message.type} from {message.source_agent} "
            f"to {message.target_agent} - {message.capability}.{message.method}"
        )
    
    async def _check_rate_limit(self, agent_id: str) -> bool:
        """Check rate limit for agent"""
        current_time = time.time()
        agent_requests = self.rate_limits[agent_id]
        
        # Remove old requests outside the window
        while agent_requests and current_time - agent_requests[0] > self.rate_limit_window:
            agent_requests.popleft()
        
        # Check if under limit
        if len(agent_requests) < self.rate_limit_max:
            agent_requests.append(current_time)
            return True
        
        return False
    
    async def _authenticate_request(self, request: MCPRequest) -> bool:
        """Authenticate request"""
        # For now, allow all requests
        # In production, implement proper authentication
        return True
    
    def register_agent(self, agent_id: str, auth_info: Dict[str, Any]):
        """Register agent for authentication"""
        self.authenticated_agents[agent_id] = auth_info
        logger.info(f"Registered agent for authentication: {agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister agent"""
        if agent_id in self.authenticated_agents:
            del self.authenticated_agents[agent_id]
        
        if agent_id in self.rate_limits:
            del self.rate_limits[agent_id]
        
        logger.info(f"Unregistered agent: {agent_id}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get middleware statistics"""
        return {
            "authenticated_agents": len(self.authenticated_agents),
            "rate_limited_agents": len(self.rate_limits),
            "rate_limit_window": self.rate_limit_window,
            "rate_limit_max": self.rate_limit_max
        }