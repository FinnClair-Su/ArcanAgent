"""
MCP Protocol Implementation
Defines the message format and protocol for Agent communication
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class MCPMessageType(str, Enum):
    """MCP message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MCPCapabilityType(str, Enum):
    """MCP capability types"""
    COGNITIVE = "cognitive"
    KNOWLEDGE = "knowledge"
    LEARNING = "learning"
    MONITORING = "monitoring"
    COORDINATION = "coordination"
    INTEGRATION = "integration"


class MCPMessage(BaseModel):
    """Base MCP message structure"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MCPMessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_agent: str
    target_agent: Optional[str] = None
    capability: str
    method: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MCPRequest(MCPMessage):
    """MCP request message"""
    type: MCPMessageType = MCPMessageType.REQUEST
    correlation_id: Optional[str] = None
    timeout: int = Field(default=30)
    
    def to_response(self, result: Any, status: str = "success") -> "MCPResponse":
        """Convert request to response"""
        return MCPResponse(
            correlation_id=self.id,
            source_agent=self.target_agent or "system",
            target_agent=self.source_agent,
            capability=self.capability,
            method=self.method,
            result=result,
            status=status,
            metadata=self.metadata
        )


class MCPResponse(MCPMessage):
    """MCP response message"""
    type: MCPMessageType = MCPMessageType.RESPONSE
    correlation_id: str
    result: Any = None
    status: str = "success"
    error: Optional[str] = None


class MCPNotification(MCPMessage):
    """MCP notification message"""
    type: MCPMessageType = MCPMessageType.NOTIFICATION
    broadcast: bool = False


class MCPError(MCPMessage):
    """MCP error message"""
    type: MCPMessageType = MCPMessageType.ERROR
    error_code: str
    error_message: str
    correlation_id: Optional[str] = None


class MCPCapability(BaseModel):
    """MCP capability definition"""
    name: str
    capability_type: MCPCapabilityType
    description: str
    methods: Dict[str, Dict[str, Any]]
    agent_id: str
    version: str = "1.0.0"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MCPProtocol:
    """MCP protocol utilities"""
    
    @staticmethod
    def serialize_message(message: MCPMessage) -> str:
        """Serialize MCP message to JSON string"""
        return message.json()
    
    @staticmethod
    def deserialize_message(data: str) -> MCPMessage:
        """Deserialize JSON string to MCP message"""
        try:
            message_dict = json.loads(data)
            message_type = message_dict.get("type")
            
            if message_type == MCPMessageType.REQUEST:
                return MCPRequest(**message_dict)
            elif message_type == MCPMessageType.RESPONSE:
                return MCPResponse(**message_dict)
            elif message_type == MCPMessageType.NOTIFICATION:
                return MCPNotification(**message_dict)
            elif message_type == MCPMessageType.ERROR:
                return MCPError(**message_dict)
            else:
                return MCPMessage(**message_dict)
        except Exception as e:
            raise ValueError(f"Invalid MCP message format: {e}")
    
    @staticmethod
    def create_capability_id(agent_id: str, capability: str) -> str:
        """Create capability ID"""
        return f"{agent_id}/{capability}"
    
    @staticmethod
    def parse_capability_id(capability_id: str) -> tuple[str, str]:
        """Parse capability ID into agent_id and capability"""
        parts = capability_id.split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid capability ID format: {capability_id}")
        return parts[0], parts[1]