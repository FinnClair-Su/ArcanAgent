"""
MCP Message Router
Routes messages between agents based on capabilities
"""

import logging
from typing import Dict, Any, Optional

from .protocol import MCPRequest, MCPResponse, MCPMessage
from .capabilities import CapabilityRegistry


logger = logging.getLogger(__name__)


class MCPRouter:
    """MCP message router"""
    
    def __init__(self, capability_registry: CapabilityRegistry):
        self.capability_registry = capability_registry
        self.route_handlers: Dict[str, Any] = {}
    
    async def route_request(self, request: MCPRequest) -> MCPResponse:
        """Route request to appropriate handler"""
        capability_id = f"{request.target_agent}/{request.capability}"
        
        # Check if capability exists
        if not await self.capability_registry.has_capability(capability_id):
            return request.to_response(
                result=None,
                status="error"
            )
        
        # Get capability handler
        handler = await self.capability_registry.get_capability_handler(capability_id)
        
        if not handler:
            return request.to_response(
                result=None,
                status="error"
            )
        
        try:
            # Execute handler
            result = await handler(request.method, request.payload)
            return request.to_response(result=result)
            
        except Exception as e:
            logger.error(f"Error executing capability handler: {e}")
            error_response = request.to_response(
                result=None,
                status="error"
            )
            error_response.error = str(e)
            return error_response
    
    def register_route_handler(self, capability: str, handler: Any):
        """Register route handler"""
        self.route_handlers[capability] = handler
    
    async def get_routing_table(self) -> Dict[str, Any]:
        """Get current routing table"""
        return await self.capability_registry.get_all_capabilities()