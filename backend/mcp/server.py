"""
MCP Server Implementation
Central hub for Agent registration and communication
"""

import asyncio
import logging
from typing import Dict, Set, Optional, Callable, Any
from websockets import WebSocketServerProtocol
from websockets.server import serve

from .protocol import MCPMessage, MCPRequest, MCPResponse, MCPNotification, MCPError, MCPProtocol
from .capabilities import CapabilityRegistry
from .middleware import MCPMiddleware
from .router import MCPRouter


logger = logging.getLogger(__name__)


class MCPServer:
    """MCP server for Agent communication"""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.agent_connections: Dict[str, str] = {}  # agent_id -> client_id
        self.capability_registry = CapabilityRegistry()
        self.middleware = MCPMiddleware()
        self.router = MCPRouter(self.capability_registry)
        self.server = None
        self.running = False
        
    async def start(self):
        """Start the MCP server"""
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        
        self.server = await serve(
            self.handle_client,
            self.host,
            self.port,
            ping_interval=20,
            ping_timeout=10
        )
        
        self.running = True
        logger.info("MCP server started successfully")
        
    async def stop(self):
        """Stop the MCP server"""
        if self.server:
            logger.info("Stopping MCP server...")
            self.running = False
            self.server.close()
            await self.server.wait_closed()
            logger.info("MCP server stopped")
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle client connections"""
        client_id = f"client_{len(self.clients)}"
        self.clients[client_id] = websocket
        
        logger.info(f"New client connected: {client_id}")
        
        try:
            async for message in websocket:
                await self.process_message(client_id, message)
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Cleanup on disconnect
            await self.cleanup_client(client_id)
    
    async def process_message(self, client_id: str, raw_message: str):
        """Process incoming message"""
        try:
            # Deserialize message
            message = MCPProtocol.deserialize_message(raw_message)
            
            # Apply middleware
            message = await self.middleware.process_incoming(message)
            
            # Route message
            if isinstance(message, MCPRequest):
                await self.handle_request(client_id, message)
            elif isinstance(message, MCPResponse):
                await self.handle_response(client_id, message)
            elif isinstance(message, MCPNotification):
                await self.handle_notification(client_id, message)
            else:
                logger.warning(f"Unknown message type: {type(message)}")
                
        except Exception as e:
            logger.error(f"Error processing message from {client_id}: {e}")
            error_msg = MCPError(
                source_agent="mcp_server",
                target_agent="unknown",
                capability="error",
                method="process_message",
                error_code="PROCESSING_ERROR",
                error_message=str(e)
            )
            await self.send_message(client_id, error_msg)
    
    async def handle_request(self, client_id: str, request: MCPRequest):
        """Handle MCP request"""
        # Register agent if this is a registration request
        if request.method == "register_agent":
            await self.register_agent(client_id, request)
            return
        
        # Route to appropriate handler
        try:
            response = await self.router.route_request(request)
            await self.send_message(client_id, response)
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            error_response = request.to_response(
                result=None,
                status="error"
            )
            error_response.error = str(e)
            await self.send_message(client_id, error_response)
    
    async def handle_response(self, client_id: str, response: MCPResponse):
        """Handle MCP response"""
        # Forward response to the appropriate client
        if response.target_agent:
            target_client = self.agent_connections.get(response.target_agent)
            if target_client and target_client in self.clients:
                await self.send_message(target_client, response)
            else:
                logger.warning(f"Target agent not found: {response.target_agent}")
    
    async def handle_notification(self, client_id: str, notification: MCPNotification):
        """Handle MCP notification"""
        if notification.broadcast:
            # Broadcast to all connected agents
            for agent_client in self.clients.values():
                if agent_client != self.clients[client_id]:
                    await self.send_message_to_websocket(agent_client, notification)
        else:
            # Send to specific target
            if notification.target_agent:
                target_client = self.agent_connections.get(notification.target_agent)
                if target_client and target_client in self.clients:
                    await self.send_message(target_client, notification)
    
    async def register_agent(self, client_id: str, request: MCPRequest):
        """Register an agent with the server"""
        try:
            agent_id = request.payload.get("agent_id")
            capabilities = request.payload.get("capabilities", [])
            
            if not agent_id:
                raise ValueError("Agent ID is required")
            
            # Store agent connection
            self.agent_connections[agent_id] = client_id
            
            # Register capabilities
            for capability in capabilities:
                await self.capability_registry.register_capability(
                    agent_id=agent_id,
                    capability=capability
                )
            
            logger.info(f"Agent registered: {agent_id}")
            
            # Send success response
            response = request.to_response(
                result={"status": "registered", "agent_id": agent_id}
            )
            await self.send_message(client_id, response)
            
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            error_response = request.to_response(
                result=None,
                status="error"
            )
            error_response.error = str(e)
            await self.send_message(client_id, error_response)
    
    async def send_message(self, client_id: str, message: MCPMessage):
        """Send message to client"""
        if client_id in self.clients:
            websocket = self.clients[client_id]
            await self.send_message_to_websocket(websocket, message)
    
    async def send_message_to_websocket(self, websocket: WebSocketServerProtocol, message: MCPMessage):
        """Send message to websocket"""
        try:
            # Apply outgoing middleware
            message = await self.middleware.process_outgoing(message)
            
            # Serialize and send
            serialized = MCPProtocol.serialize_message(message)
            await websocket.send(serialized)
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def cleanup_client(self, client_id: str):
        """Cleanup client connection"""
        # Remove from clients
        if client_id in self.clients:
            del self.clients[client_id]
        
        # Remove agent connection
        agent_id = None
        for aid, cid in self.agent_connections.items():
            if cid == client_id:
                agent_id = aid
                break
        
        if agent_id:
            del self.agent_connections[agent_id]
            # Unregister capabilities
            await self.capability_registry.unregister_agent(agent_id)
            logger.info(f"Agent disconnected: {agent_id}")
    
    def get_connected_agents(self) -> Set[str]:
        """Get list of connected agents"""
        return set(self.agent_connections.keys())
    
    def get_agent_capabilities(self, agent_id: str) -> Dict[str, Any]:
        """Get capabilities for an agent"""
        return self.capability_registry.get_agent_capabilities(agent_id)