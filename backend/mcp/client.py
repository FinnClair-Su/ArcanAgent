"""
MCP Client Implementation
Client for Agent-to-Agent communication via MCP protocol
"""

import asyncio
import logging
from typing import Dict, Optional, Any, Callable
from websockets import connect, WebSocketClientProtocol

from .protocol import MCPMessage, MCPRequest, MCPResponse, MCPNotification, MCPProtocol


logger = logging.getLogger(__name__)


class MCPClient:
    """MCP client for Agent communication"""
    
    def __init__(self, agent_id: str, server_url: str = "ws://localhost:8080"):
        self.agent_id = agent_id
        self.server_url = server_url
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.notification_handlers: Dict[str, Callable] = {}
        
    async def connect(self):
        """Connect to MCP server"""
        try:
            logger.info(f"Connecting to MCP server: {self.server_url}")
            self.websocket = await connect(self.server_url)
            self.connected = True
            
            # Start message handling task
            asyncio.create_task(self._handle_messages())
            
            logger.info(f"Connected to MCP server: {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info(f"Disconnected from MCP server: {self.agent_id}")
    
    async def register_agent(self, capabilities: list):
        """Register agent with server"""
        request = MCPRequest(
            source_agent=self.agent_id,
            target_agent="mcp_server",
            capability="registration",
            method="register_agent",
            payload={
                "agent_id": self.agent_id,
                "capabilities": capabilities
            }
        )
        
        response = await self.send_request(request)
        if response.status != "success":
            raise RuntimeError(f"Failed to register agent: {response.error}")
        
        return response.result
    
    async def send_request(self, request: MCPRequest) -> MCPResponse:
        """Send request and wait for response"""
        if not self.connected or not self.websocket:
            raise RuntimeError("Not connected to MCP server")
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request.id] = future
        
        try:
            # Send request
            serialized = MCPProtocol.serialize_message(request)
            await self.websocket.send(serialized)
            
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=request.timeout)
            return response
            
        except asyncio.TimeoutError:
            # Clean up pending request
            if request.id in self.pending_requests:
                del self.pending_requests[request.id]
            raise RuntimeError(f"Request timeout: {request.id}")
        
        except Exception as e:
            # Clean up pending request
            if request.id in self.pending_requests:
                del self.pending_requests[request.id]
            raise RuntimeError(f"Request failed: {e}")
    
    async def call_agent_method(self, target_agent: str, capability: str, method: str, **kwargs) -> Any:
        """Call method on another agent"""
        request = MCPRequest(
            source_agent=self.agent_id,
            target_agent=target_agent,
            capability=capability,
            method=method,
            payload=kwargs
        )
        
        response = await self.send_request(request)
        if response.status != "success":
            raise RuntimeError(f"Agent method call failed: {response.error}")
        
        return response.result
    
    async def send_notification(self, target_agent: Optional[str], capability: str, method: str, broadcast: bool = False, **kwargs):
        """Send notification to agent(s)"""
        notification = MCPNotification(
            source_agent=self.agent_id,
            target_agent=target_agent,
            capability=capability,
            method=method,
            payload=kwargs,
            broadcast=broadcast
        )
        
        if not self.connected or not self.websocket:
            raise RuntimeError("Not connected to MCP server")
        
        serialized = MCPProtocol.serialize_message(notification)
        await self.websocket.send(serialized)
    
    def register_message_handler(self, capability: str, method: str, handler: Callable):
        """Register handler for incoming messages"""
        key = f"{capability}.{method}"
        self.message_handlers[key] = handler
    
    def register_notification_handler(self, capability: str, method: str, handler: Callable):
        """Register handler for incoming notifications"""
        key = f"{capability}.{method}"
        self.notification_handlers[key] = handler
    
    async def _handle_messages(self):
        """Handle incoming messages"""
        try:
            async for raw_message in self.websocket:
                await self._process_message(raw_message)
        except Exception as e:
            logger.error(f"Error handling messages: {e}")
            self.connected = False
    
    async def _process_message(self, raw_message: str):
        """Process incoming message"""
        try:
            message = MCPProtocol.deserialize_message(raw_message)
            
            if isinstance(message, MCPResponse):
                await self._handle_response(message)
            elif isinstance(message, MCPRequest):
                await self._handle_request(message)
            elif isinstance(message, MCPNotification):
                await self._handle_notification(message)
            else:
                logger.warning(f"Unknown message type: {type(message)}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def _handle_response(self, response: MCPResponse):
        """Handle response message"""
        if response.correlation_id in self.pending_requests:
            future = self.pending_requests.pop(response.correlation_id)
            future.set_result(response)
    
    async def _handle_request(self, request: MCPRequest):
        """Handle request message"""
        key = f"{request.capability}.{request.method}"
        
        if key in self.message_handlers:
            try:
                handler = self.message_handlers[key]
                result = await handler(request.payload)
                
                # Send response
                response = request.to_response(result=result)
                await self._send_response(response)
                
            except Exception as e:
                logger.error(f"Error handling request: {e}")
                error_response = request.to_response(
                    result=None,
                    status="error"
                )
                error_response.error = str(e)
                await self._send_response(error_response)
        else:
            logger.warning(f"No handler for request: {key}")
            error_response = request.to_response(
                result=None,
                status="error"
            )
            error_response.error = f"No handler for method: {request.method}"
            await self._send_response(error_response)
    
    async def _handle_notification(self, notification: MCPNotification):
        """Handle notification message"""
        key = f"{notification.capability}.{notification.method}"
        
        if key in self.notification_handlers:
            try:
                handler = self.notification_handlers[key]
                await handler(notification.payload)
            except Exception as e:
                logger.error(f"Error handling notification: {e}")
        else:
            logger.debug(f"No handler for notification: {key}")
    
    async def _send_response(self, response: MCPResponse):
        """Send response message"""
        if self.connected and self.websocket:
            serialized = MCPProtocol.serialize_message(response)
            await self.websocket.send(serialized)