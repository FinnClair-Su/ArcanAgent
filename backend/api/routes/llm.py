"""
LLM API Routes

Provides endpoints for testing and managing LLM connections.
Allows testing different providers and getting provider status.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from backend.core import (
    LLMMessage, 
    get_llm_client_manager, 
    get_provider_status,
    test_llm_client,
    chat_completion
)
from backend.config import config

router = APIRouter()
logger = logging.getLogger("ArcanAgent.API.LLM")


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat completion request."""
    messages: List[Dict[str, str]]
    client_name: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat completion response."""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    response_time: Optional[float] = None


class TestResponse(BaseModel):
    """LLM test response."""
    success: bool
    client_name: str
    model: Optional[str] = None
    provider: Optional[str] = None
    response_content: Optional[str] = None
    response_time: Optional[float] = None
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None
    error_type: Optional[str] = None


@router.get("/providers")
async def get_providers_status() -> Dict[str, Any]:
    """
    Get the status of all LLM providers.
    
    Returns:
        Dict containing status information for each provider
    """
    logger.info("Getting LLM providers status")
    
    try:
        providers_status = get_provider_status(config)
        
        # Add manager information
        manager = get_llm_client_manager()
        available_clients = manager.list_clients()
        default_client = manager.default_client
        
        return {
            "providers": providers_status,
            "available_clients": available_clients,
            "default_client": default_client,
            "total_configured": len([p for p in providers_status.values() if p["configured"]]),
            "total_available": len(available_clients)
        }
        
    except Exception as e:
        logger.error(f"Error getting providers status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting providers status: {str(e)}")


@router.get("/clients")
async def list_clients() -> Dict[str, Any]:
    """
    List all available LLM clients.
    
    Returns:
        Dict containing client information
    """
    logger.info("Listing LLM clients")
    
    try:
        manager = get_llm_client_manager()
        
        return {
            "clients": manager.list_clients(),
            "default_client": manager.default_client,
            "total_clients": len(manager.clients)
        }
        
    except Exception as e:
        logger.error(f"Error listing clients: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing clients: {str(e)}")


@router.post("/test/{client_name}")
async def test_client(client_name: str) -> TestResponse:
    """
    Test a specific LLM client.
    
    Args:
        client_name: Name of the client to test
        
    Returns:
        Test results
    """
    logger.info(f"Testing LLM client: {client_name}")
    
    try:
        result = await test_llm_client(client_name)
        return TestResponse(**result)
        
    except Exception as e:
        logger.error(f"Error testing client {client_name}: {e}")
        return TestResponse(
            success=False,
            client_name=client_name,
            error=str(e),
            error_type=type(e).__name__
        )


@router.post("/test")
async def test_default_client() -> TestResponse:
    """
    Test the default LLM client.
    
    Returns:
        Test results
    """
    logger.info("Testing default LLM client")
    
    try:
        result = await test_llm_client()
        return TestResponse(**result)
        
    except Exception as e:
        logger.error(f"Error testing default client: {e}")
        return TestResponse(
            success=False,
            client_name="default",
            error=str(e),
            error_type=type(e).__name__
        )


@router.post("/chat")
async def chat_with_llm(request: ChatRequest) -> ChatResponse:
    """
    Chat with an LLM.
    
    Args:
        request: Chat request with messages and optional client name
        
    Returns:
        Chat response
    """
    logger.info(f"Chat request with {len(request.messages)} messages using client: {request.client_name or 'default'}")
    
    try:
        # Convert dict messages to LLMMessage objects
        llm_messages = [
            LLMMessage(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                name=msg.get("name")
            )
            for msg in request.messages
        ]
        
        # Validate messages
        if not llm_messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        for msg in llm_messages:
            if not msg.content.strip():
                raise HTTPException(status_code=400, detail="Empty message content")
            if msg.role not in ["system", "user", "assistant"]:
                raise HTTPException(status_code=400, detail=f"Invalid message role: {msg.role}")
        
        # Get chat completion
        response = await chat_completion(
            messages=llm_messages,
            client_name=request.client_name,
            stream=request.stream  # Note: streaming not implemented in this endpoint
        )
        
        return ChatResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            usage=response.usage,
            response_time=response.response_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=f"Error in chat completion: {str(e)}")


@router.post("/chat/stream")
async def chat_with_llm_stream(request: ChatRequest):
    """
    Stream chat with an LLM.
    
    Args:
        request: Chat request with messages and optional client name
        
    Returns:
        Streaming response
    """
    logger.info(f"Streaming chat request with {len(request.messages)} messages using client: {request.client_name or 'default'}")
    
    from fastapi.responses import StreamingResponse
    import json
    
    try:
        # Convert dict messages to LLMMessage objects
        llm_messages = [
            LLMMessage(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                name=msg.get("name")
            )
            for msg in request.messages
        ]
        
        # Validate messages
        if not llm_messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        async def generate_stream():
            try:
                stream = await chat_completion(
                    messages=llm_messages,
                    client_name=request.client_name,
                    stream=True
                )
                
                async for chunk in stream:
                    # Send each chunk as JSON
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                # Send error
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in streaming chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error in streaming chat: {str(e)}")


@router.get("/health")
async def llm_health_check() -> Dict[str, Any]:
    """
    Health check for LLM services.
    
    Returns:
        Health status of all LLM providers
    """
    logger.info("LLM health check")
    
    try:
        manager = get_llm_client_manager()
        providers_status = get_provider_status(config)
        
        # Test default client if available
        default_test_result = None
        if manager.default_client:
            try:
                default_test_result = await test_llm_client()
            except Exception as e:
                default_test_result = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "status": "healthy" if manager.default_client else "degraded",
            "providers": providers_status,
            "available_clients": manager.list_clients(),
            "default_client": manager.default_client,
            "default_client_test": default_test_result,
            "total_configured": len([p for p in providers_status.values() if p["configured"]]),
            "timestamp": "2024-01-01T00:00:00Z"  # Will be replaced with actual timestamp
        }
        
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }