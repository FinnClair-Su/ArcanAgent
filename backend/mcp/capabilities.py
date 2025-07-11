"""
MCP Capability Registry
Manages Agent capabilities and method registration
"""

import logging
from typing import Dict, Any, Optional, Set, Callable
from datetime import datetime

from .protocol import MCPCapability, MCPCapabilityType


logger = logging.getLogger(__name__)


class CapabilityRegistry:
    """Registry for Agent capabilities"""
    
    def __init__(self):
        self.capabilities: Dict[str, MCPCapability] = {}
        self.capability_handlers: Dict[str, Callable] = {}
        self.agent_capabilities: Dict[str, Set[str]] = {}
    
    async def register_capability(self, agent_id: str, capability: Dict[str, Any]):
        """Register a capability for an agent"""
        capability_name = capability.get("name")
        if not capability_name:
            raise ValueError("Capability name is required")
        
        capability_id = f"{agent_id}/{capability_name}"
        
        mcp_capability = MCPCapability(
            name=capability_name,
            capability_type=MCPCapabilityType(capability.get("type", "cognitive")),
            description=capability.get("description", ""),
            methods=capability.get("methods", {}),
            agent_id=agent_id,
            version=capability.get("version", "1.0.0")
        )
        
        self.capabilities[capability_id] = mcp_capability
        
        # Track agent capabilities
        if agent_id not in self.agent_capabilities:
            self.agent_capabilities[agent_id] = set()
        self.agent_capabilities[agent_id].add(capability_id)
        
        logger.info(f"Registered capability: {capability_id}")
    
    async def unregister_capability(self, capability_id: str):
        """Unregister a capability"""
        if capability_id in self.capabilities:
            capability = self.capabilities[capability_id]
            agent_id = capability.agent_id
            
            # Remove from registry
            del self.capabilities[capability_id]
            
            # Remove from agent capabilities
            if agent_id in self.agent_capabilities:
                self.agent_capabilities[agent_id].discard(capability_id)
                if not self.agent_capabilities[agent_id]:
                    del self.agent_capabilities[agent_id]
            
            # Remove handler
            if capability_id in self.capability_handlers:
                del self.capability_handlers[capability_id]
            
            logger.info(f"Unregistered capability: {capability_id}")
    
    async def unregister_agent(self, agent_id: str):
        """Unregister all capabilities for an agent"""
        if agent_id in self.agent_capabilities:
            capabilities = self.agent_capabilities[agent_id].copy()
            for capability_id in capabilities:
                await self.unregister_capability(capability_id)
            
            logger.info(f"Unregistered all capabilities for agent: {agent_id}")
    
    async def has_capability(self, capability_id: str) -> bool:
        """Check if capability exists"""
        return capability_id in self.capabilities
    
    async def get_capability(self, capability_id: str) -> Optional[MCPCapability]:
        """Get capability by ID"""
        return self.capabilities.get(capability_id)
    
    async def get_agent_capabilities(self, agent_id: str) -> Set[str]:
        """Get all capabilities for an agent"""
        return self.agent_capabilities.get(agent_id, set())
    
    async def get_all_capabilities(self) -> Dict[str, MCPCapability]:
        """Get all registered capabilities"""
        return self.capabilities.copy()
    
    async def find_capabilities_by_type(self, capability_type: MCPCapabilityType) -> Dict[str, MCPCapability]:
        """Find capabilities by type"""
        return {
            cap_id: cap
            for cap_id, cap in self.capabilities.items()
            if cap.capability_type == capability_type
        }
    
    async def find_capabilities_by_method(self, method: str) -> Dict[str, MCPCapability]:
        """Find capabilities that support a specific method"""
        return {
            cap_id: cap
            for cap_id, cap in self.capabilities.items()
            if method in cap.methods
        }
    
    def register_capability_handler(self, capability_id: str, handler: Callable):
        """Register handler for capability"""
        self.capability_handlers[capability_id] = handler
        logger.info(f"Registered handler for capability: {capability_id}")
    
    async def get_capability_handler(self, capability_id: str) -> Optional[Callable]:
        """Get handler for capability"""
        return self.capability_handlers.get(capability_id)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_capabilities": len(self.capabilities),
            "total_agents": len(self.agent_capabilities),
            "capabilities_by_type": {
                cap_type.value: len(await self.find_capabilities_by_type(cap_type))
                for cap_type in MCPCapabilityType
            },
            "agents_by_capability_count": {
                agent_id: len(capabilities)
                for agent_id, capabilities in self.agent_capabilities.items()
            }
        }