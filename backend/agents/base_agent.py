"""
Base Agent Class
Foundation for all ArcanAgent agents with MCP communication
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable

from backend.mcp import MCPClient, MCPCapability, MCPCapabilityType
from backend.settings import settings


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all ArcanAgent agents"""
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.mcp_client = MCPClient(agent_id, f"ws://{settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}")
        self.capabilities: List[MCPCapability] = []
        self.running = False
        self.state: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize the agent"""
        logger.info(f"Initializing agent: {self.name}")
        
        # Connect to MCP server
        await self.mcp_client.connect()
        
        # Register capabilities
        await self._register_capabilities()
        
        # Register with MCP server
        await self.mcp_client.register_agent(self._get_capability_definitions())
        
        # Setup message handlers
        await self._setup_handlers()
        
        # Custom initialization
        await self._initialize()
        
        self.running = True
        logger.info(f"Agent initialized: {self.name}")
    
    async def shutdown(self):
        """Shutdown the agent"""
        logger.info(f"Shutting down agent: {self.name}")
        
        self.running = False
        
        # Custom shutdown
        await self._shutdown()
        
        # Disconnect from MCP
        await self.mcp_client.disconnect()
        
        logger.info(f"Agent shut down: {self.name}")
    
    @abstractmethod
    async def _initialize(self):
        """Custom initialization logic"""
        pass
    
    @abstractmethod
    async def _shutdown(self):
        """Custom shutdown logic"""
        pass
    
    @abstractmethod
    async def _register_capabilities(self):
        """Register agent capabilities"""
        pass
    
    async def _setup_handlers(self):
        """Setup MCP message handlers"""
        for capability in self.capabilities:
            for method_name in capability.methods:
                handler = getattr(self, method_name, None)\n                if handler:\n                    self.mcp_client.register_message_handler(\n                        capability.name,\n                        method_name,\n                        handler\n                    )\n    \n    def _get_capability_definitions(self) -> List[Dict[str, Any]]:\n        \"\"\"Get capability definitions for MCP registration\"\"\"\n        return [\n            {\n                \"name\": cap.name,\n                \"type\": cap.capability_type.value,\n                \"description\": cap.description,\n                \"methods\": cap.methods,\n                \"version\": cap.version\n            }\n            for cap in self.capabilities\n        ]\n    \n    async def call_agent_method(self, target_agent: str, capability: str, method: str, **kwargs) -> Any:\n        \"\"\"Call method on another agent\"\"\"\n        return await self.mcp_client.call_agent_method(target_agent, capability, method, **kwargs)\n    \n    async def send_notification(self, target_agent: Optional[str], capability: str, method: str, broadcast: bool = False, **kwargs):\n        \"\"\"Send notification to agent(s)\"\"\"\n        await self.mcp_client.send_notification(target_agent, capability, method, broadcast, **kwargs)\n    \n    async def update_state(self, key: str, value: Any):\n        \"\"\"Update agent state\"\"\"\n        self.state[key] = value\n        logger.debug(f\"Agent {self.name} state updated: {key} = {value}\")\n    \n    async def get_state(self, key: str) -> Any:\n        \"\"\"Get agent state\"\"\"\n        return self.state.get(key)\n    \n    async def get_agent_info(self) -> Dict[str, Any]:\n        \"\"\"Get agent information\"\"\"\n        return {\n            \"agent_id\": self.agent_id,\n            \"name\": self.name,\n            \"description\": self.description,\n            \"running\": self.running,\n            \"capabilities\": self._get_capability_definitions(),\n            \"state\": self.state\n        }\n    \n    async def health_check(self) -> Dict[str, Any]:\n        \"\"\"Health check for agent\"\"\"\n        return {\n            \"agent_id\": self.agent_id,\n            \"name\": self.name,\n            \"status\": \"healthy\" if self.running else \"stopped\",\n            \"connected_to_mcp\": self.mcp_client.connected\n        }"