"""
Complete Learning Flow API Routes - SPEC Compliant

Implements the full learning flow with integrated Arcana Agent system:
1. Knowledge Assessment (The High Priestess) 🔮
2. Learning Path Planning (The Hermit) 🏮
3. Content Generation (The Magician) ✨
4. Understanding Evaluation (Justice) ⚖️
5. Memory Consolidation (The Empress) 🌸

Features:
- SPEC-compliant tool calling engine integration
- Full agent orchestration support
- WebSocket support for real-time progress
- Session management and persistence
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi import Request
from pydantic import BaseModel, Field
import json

# Core system imports
from ...core.bidirectional_links import BidirectionalLinkEngine  
from ...core.context_manager import ContextManager
from ...core.tool_call_engine import ToolCallEngine, create_tool_engine
from ...core.llm_client import get_llm_client, LLMMessage
from ...agents import (
    TheHighPriestess, TheHermit, TheMagician, Justice, TheEmpress,
    ArcanaAgentOrchestrator, OrchestrationResult
)

router = APIRouter()
logger = logging.getLogger("ArcanAgent.API.Learning")

# Session storage (in production, use Redis or database)
active_sessions: Dict[str, Dict[str, Any]] = {}
websocket_connections: Dict[str, WebSocket] = {}


# Request/Response Models
class LearningRequest(BaseModel):
    """Base learning request model."""
    user_query: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class LearningResponse(BaseModel):
    """Base learning response model."""
    success: bool
    session_id: str
    agent_name: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    execution_time: float = 0.0
    links_discovered: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class OrchestrationRequest(BaseModel):
    """Request for complete learning orchestration."""
    user_query: str
    session_id: Optional[str] = None
    enable_websocket: bool = False


class OrchestrationResponse(BaseModel):
    """Response for complete learning orchestration."""
    success: bool
    session_id: str
    total_execution_time: float
    agents_executed: int
    final_content: str
    consolidated_links: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


# Dependency injection functions
async def get_core_systems(request: Request) -> Dict[str, Any]:
    """Get core system dependencies."""
    return {
        "link_engine": request.app.state.link_engine,
        "context_manager": request.app.state.context_manager,
        "tool_engine": request.app.state.tool_engine,
        "llm_manager": request.app.state.llm_manager
    }


async def get_agent_orchestrator(core_systems: Dict[str, Any] = Depends(get_core_systems)) -> ArcanaAgentOrchestrator:
    """Get the agent orchestrator with all systems initialized."""
    link_engine = core_systems["link_engine"]
    context_manager = core_systems["context_manager"]
    tool_engine = core_systems["tool_engine"]
    
    orchestrator = ArcanaAgentOrchestrator(
        link_engine=link_engine,
        context_manager=context_manager,
        tool_engine=tool_engine
    )
    
    return orchestrator


def create_session(user_query: str) -> str:
    """Create a new learning session."""
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "session_id": session_id,
        "user_query": user_query,
        "status": "active",
        "current_stage": "initialized",
        "stages_completed": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "results": {}
    }
    return session_id


async def notify_websocket(session_id: str, message: Dict[str, Any]):
    """Send message to WebSocket if connected."""
    if session_id in websocket_connections:
        try:
            await websocket_connections[session_id].send_text(json.dumps(message))
        except Exception as e:
            logger.warning(f"Failed to send WebSocket message: {e}")


# Individual Agent Endpoints
@router.post("/assess-knowledge", response_model=LearningResponse)
async def assess_knowledge(
    request: LearningRequest,
    core_systems: Dict[str, Any] = Depends(get_core_systems)
):
    """
    Assess knowledge using The High Priestess agent 🔮
    
    Analyzes current knowledge state through bidirectional link analysis
    and provides insights about learning readiness and knowledge gaps.
    """
    session_id = request.session_id or create_session(request.user_query)
    
    try:
        # Get The High Priestess agent
        link_engine = core_systems["link_engine"]
        context_manager = core_systems["context_manager"]
        tool_engine = core_systems["tool_engine"]
        
        priestess = TheHighPriestess(link_engine, context_manager, tool_engine)
        
        # Execute knowledge assessment
        result = await priestess._execute_with_monitoring(
            user_query=request.user_query,
            context=request.context,
            llm_client=get_llm_client()
        )
        
        # Update session
        if session_id in active_sessions:
            active_sessions[session_id]["current_stage"] = "assessment_complete"
            active_sessions[session_id]["stages_completed"].append("assessment")
            active_sessions[session_id]["results"]["assessment"] = result
            active_sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Send WebSocket notification
        await notify_websocket(session_id, {
            "type": "stage_complete",
            "stage": "assessment",
            "agent": "the_high_priestess",
            "success": result.success
        })
        
        return LearningResponse(
            success=result.success,
            session_id=session_id,
            agent_name=result.agent_name,
            content=result.content,
            metadata=result.metadata,
            confidence=result.confidence,
            execution_time=result.execution_time,
            links_discovered=list(result.links_discovered),
            errors=result.errors
        )
        
    except Exception as e:
        logger.error(f"Knowledge assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.post("/plan-path", response_model=LearningResponse)
async def plan_learning_path(
    request: LearningRequest,
    core_systems: Dict[str, Any] = Depends(get_core_systems)
):
    """
    Plan learning path using The Hermit agent 🏮
    
    Creates optimal learning sequences within the Zone of Proximal Development
    based on current knowledge assessment and bidirectional link analysis.
    """
    session_id = request.session_id or create_session(request.user_query)
    
    try:
        # Get systems
        link_engine = core_systems["link_engine"]
        context_manager = core_systems["context_manager"]
        tool_engine = core_systems["tool_engine"]
        
        hermit = TheHermit(link_engine, context_manager, tool_engine)
        
        # Get context from previous assessment
        context = request.context or {}
        if session_id in active_sessions and "assessment" in active_sessions[session_id]["results"]:
            assessment_result = active_sessions[session_id]["results"]["assessment"]
            context["high_priestess_assessment"] = assessment_result.metadata
        
        # Execute path planning
        result = await hermit._execute_with_monitoring(
            user_query=request.user_query,
            context=context,
            llm_client=get_llm_client()
        )
        
        # Update session
        if session_id in active_sessions:
            active_sessions[session_id]["current_stage"] = "planning_complete"
            active_sessions[session_id]["stages_completed"].append("planning")
            active_sessions[session_id]["results"]["planning"] = result
            active_sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()
        
        await notify_websocket(session_id, {
            "type": "stage_complete",
            "stage": "planning",
            "agent": "the_hermit",
            "success": result.success
        })
        
        return LearningResponse(
            success=result.success,
            session_id=session_id,
            agent_name=result.agent_name,
            content=result.content,
            metadata=result.metadata,
            confidence=result.confidence,
            execution_time=result.execution_time,
            links_discovered=list(result.links_discovered),
            errors=result.errors
        )
        
    except Exception as e:
        logger.error(f"Path planning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Path planning failed: {str(e)}")


@router.post("/generate-content", response_model=LearningResponse)
async def generate_content(
    request: LearningRequest,
    core_systems: Dict[str, Any] = Depends(get_core_systems)
):
    """
    Generate content using The Magician agent ✨
    
    Creates personalized learning content with automatic bidirectional
    link weaving based on assessment and learning path.
    """
    session_id = request.session_id or create_session(request.user_query)
    
    try:
        # Get systems
        link_engine = core_systems["link_engine"]
        context_manager = core_systems["context_manager"]
        tool_engine = core_systems["tool_engine"]
        
        magician = TheMagician(link_engine, context_manager, tool_engine)
        
        # Build context from previous stages
        context = request.context or {}
        if session_id in active_sessions:
            session_results = active_sessions[session_id]["results"]
            if "assessment" in session_results:
                context["high_priestess_assessment"] = session_results["assessment"].metadata
            if "planning" in session_results:
                context["hermit_plan"] = session_results["planning"].metadata
        
        # Execute content generation
        result = await magician._execute_with_monitoring(
            user_query=request.user_query,
            context=context,
            llm_client=get_llm_client()
        )
        
        # Update session
        if session_id in active_sessions:
            active_sessions[session_id]["current_stage"] = "content_complete"
            active_sessions[session_id]["stages_completed"].append("content")
            active_sessions[session_id]["results"]["content"] = result
            active_sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()
        
        await notify_websocket(session_id, {
            "type": "stage_complete",
            "stage": "content",
            "agent": "the_magician",
            "success": result.success,
            "links_created": len(result.links_discovered)
        })
        
        return LearningResponse(
            success=result.success,
            session_id=session_id,
            agent_name=result.agent_name,
            content=result.content,
            metadata=result.metadata,
            confidence=result.confidence,
            execution_time=result.execution_time,
            links_discovered=list(result.links_discovered),
            errors=result.errors
        )
        
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@router.post("/evaluate-understanding", response_model=LearningResponse)
async def evaluate_understanding(
    request: LearningRequest,
    core_systems: Dict[str, Any] = Depends(get_core_systems)
):
    """
    Evaluate understanding using Justice agent ⚖️
    
    Provides fair assessment of comprehension and learning progress
    through multiple evaluation methods and targeted feedback.
    """
    session_id = request.session_id or create_session(request.user_query)
    
    try:
        # Get systems
        link_engine = core_systems["link_engine"]
        context_manager = core_systems["context_manager"]
        tool_engine = core_systems["tool_engine"]
        
        justice = Justice(link_engine, context_manager, tool_engine)
        
        # Build context from all previous stages
        context = request.context or {}
        if session_id in active_sessions:
            session_results = active_sessions[session_id]["results"]
            if "assessment" in session_results:
                context["high_priestess_assessment"] = session_results["assessment"].metadata
            if "planning" in session_results:
                context["hermit_plan"] = session_results["planning"].metadata
            if "content" in session_results:
                context["magician_content"] = session_results["content"].metadata
        
        # Execute understanding evaluation
        result = await justice._execute_with_monitoring(
            user_query=request.user_query,
            context=context,
            llm_client=get_llm_client()
        )
        
        # Update session
        if session_id in active_sessions:
            active_sessions[session_id]["current_stage"] = "evaluation_complete"
            active_sessions[session_id]["stages_completed"].append("evaluation")
            active_sessions[session_id]["results"]["evaluation"] = result
            active_sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()
        
        await notify_websocket(session_id, {
            "type": "stage_complete",
            "stage": "evaluation",
            "agent": "justice",
            "success": result.success,
            "confidence": result.confidence
        })
        
        return LearningResponse(
            success=result.success,
            session_id=session_id,
            agent_name=result.agent_name,
            content=result.content,
            metadata=result.metadata,
            confidence=result.confidence,
            execution_time=result.execution_time,
            links_discovered=list(result.links_discovered),
            errors=result.errors
        )
        
    except Exception as e:
        logger.error(f"Understanding evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Understanding evaluation failed: {str(e)}")


@router.post("/consolidate-memory", response_model=LearningResponse)
async def consolidate_memory(
    request: LearningRequest,
    core_systems: Dict[str, Any] = Depends(get_core_systems)
):
    """
    Consolidate memory using The Empress agent 🌸
    
    Integrates learning into lasting memory structures and strengthens
    the bidirectional link network for enhanced recall.
    """
    session_id = request.session_id or create_session(request.user_query)
    
    try:
        # Get systems
        link_engine = core_systems["link_engine"]
        context_manager = core_systems["context_manager"]
        tool_engine = core_systems["tool_engine"]
        
        empress = TheEmpress(link_engine, context_manager, tool_engine)
        
        # Build complete context from all stages
        context = request.context or {}
        if session_id in active_sessions:
            session_results = active_sessions[session_id]["results"]
            if "assessment" in session_results:
                context["high_priestess_assessment"] = session_results["assessment"].metadata
            if "planning" in session_results:
                context["hermit_plan"] = session_results["planning"].metadata
            if "content" in session_results:
                context["magician_content"] = session_results["content"].metadata
            if "evaluation" in session_results:
                context["justice_evaluation"] = session_results["evaluation"].metadata
        
        # Execute memory consolidation
        result = await empress._execute_with_monitoring(
            user_query=request.user_query,
            context=context,
            llm_client=get_llm_client()
        )
        
        # Update session
        if session_id in active_sessions:
            active_sessions[session_id]["current_stage"] = "consolidation_complete"
            active_sessions[session_id]["stages_completed"].append("consolidation")
            active_sessions[session_id]["results"]["consolidation"] = result
            active_sessions[session_id]["status"] = "completed"
            active_sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()
        
        await notify_websocket(session_id, {
            "type": "session_complete",
            "stage": "consolidation",
            "agent": "the_empress",
            "success": result.success,
            "total_links": len(result.links_discovered)
        })
        
        return LearningResponse(
            success=result.success,
            session_id=session_id,
            agent_name=result.agent_name,
            content=result.content,
            metadata=result.metadata,
            confidence=result.confidence,
            execution_time=result.execution_time,
            links_discovered=list(result.links_discovered),
            errors=result.errors
        )
        
    except Exception as e:
        logger.error(f"Memory consolidation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Memory consolidation failed: {str(e)}")


# Complete Orchestration Endpoint
@router.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate_complete_learning(
    request: OrchestrationRequest,
    orchestrator: ArcanaAgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    Run complete learning orchestration through all five agents.
    
    Executes the full learning pipeline:
    🔮 Assessment → 🏮 Planning → ✨ Content → ⚖️ Evaluation → 🌸 Consolidation
    """
    session_id = request.session_id or create_session(request.user_query)
    
    try:
        logger.info(f"Starting complete learning orchestration for session: {session_id}")
        
        # Send initial WebSocket notification
        if request.enable_websocket:
            await notify_websocket(session_id, {
                "type": "orchestration_start",
                "session_id": session_id,
                "total_stages": 5
            })
        
        # Execute complete orchestration
        result: OrchestrationResult = await orchestrator.orchestrate_learning(
            user_query=request.user_query,
            context=None
        )
        
        # Update session with complete results
        if session_id in active_sessions:
            active_sessions[session_id]["status"] = "completed" if result.success else "failed"
            active_sessions[session_id]["current_stage"] = "orchestration_complete"
            active_sessions[session_id]["results"]["orchestration"] = result
            active_sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()
        
        # Final WebSocket notification
        if request.enable_websocket:
            await notify_websocket(session_id, {
                "type": "orchestration_complete",
                "session_id": session_id,
                "success": result.success,
                "total_time": result.total_execution_time,
                "agents_executed": len(result.agent_responses)
            })
        
        return OrchestrationResponse(
            success=result.success,
            session_id=session_id,
            total_execution_time=result.total_execution_time,
            agents_executed=len(result.agent_responses),
            final_content=result.final_content,
            consolidated_links=list(result.consolidated_links),
            metadata=result.pipeline_metadata,
            errors=result.errors
        )
        
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        
        # Error WebSocket notification
        if request.enable_websocket:
            await notify_websocket(session_id, {
                "type": "orchestration_error",
                "session_id": session_id,
                "error": str(e)
            })
        
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")


# Tool Call Engine Integration
@router.post("/tool-call")
async def handle_tool_call(
    request: Dict[str, Any],
    core_systems: Dict[str, Any] = Depends(get_core_systems)
):
    """
    Handle SPEC-compliant tool calls using the NagaAgent format.
    
    Supports the <<<[TOOL_REQUEST]>>> format for calling Arcana Agents.
    """
    try:
        user_message = request.get("message", "")
        session_id = request.get("session_id")
        
        # Get tool engine and register Arcana agents
        tool_engine = core_systems["tool_engine"]
        link_engine = core_systems["link_engine"]
        context_manager = core_systems["context_manager"]
        
        # Create and register agents if not already done
        agents = {
            "the_high_priestess": TheHighPriestess(link_engine, context_manager, tool_engine),
            "the_hermit": TheHermit(link_engine, context_manager, tool_engine),
            "the_magician": TheMagician(link_engine, context_manager, tool_engine),
            "justice": Justice(link_engine, context_manager, tool_engine),
            "the_empress": TheEmpress(link_engine, context_manager, tool_engine)
        }
        
        for name, agent in agents.items():
            tool_engine.register_arcana_agent(name, agent)
        
        # Handle tool call loop
        messages = [LLMMessage(role="user", content=user_message)]
        result = await tool_engine.handle_tool_call_loop(
            messages=messages,
            llm_client=get_llm_client()
        )
        
        return {
            "success": result["success"],
            "content": result["content"],
            "recursion_depth": result["recursion_depth"],
            "tool_calls_made": len(result["tool_calls_made"]),
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        raise HTTPException(status_code=500, detail=f"Tool call failed: {str(e)}")


# Session Management
@router.get("/session/{session_id}")
async def get_learning_session(session_id: str):
    """Get complete learning session information."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return active_sessions[session_id]


@router.get("/sessions")
async def list_learning_sessions():
    """List all active learning sessions."""
    return {
        "sessions": list(active_sessions.values()),
        "total_count": len(active_sessions)
    }


@router.delete("/session/{session_id}")
async def delete_learning_session(session_id: str):
    """Delete a learning session."""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Close WebSocket connection if exists
    if session_id in websocket_connections:
        try:
            await websocket_connections[session_id].close()
            del websocket_connections[session_id]
        except:
            pass
    
    del active_sessions[session_id]
    return {"message": "Session deleted successfully"}


# WebSocket Support
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time learning progress updates."""
    await websocket.accept()
    websocket_connections[session_id] = websocket
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive and handle messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle ping/pong for connection keep-alive
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.warning(f"WebSocket message handling error: {e}")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    finally:
        # Clean up connection
        if session_id in websocket_connections:
            del websocket_connections[session_id]


# System Status Endpoint
@router.get("/status")
async def get_learning_system_status(
    core_systems: Dict[str, Any] = Depends(get_core_systems)
):
    """Get learning system status and statistics."""
    try:
        link_engine = core_systems["link_engine"]
        context_manager = core_systems["context_manager"]
        tool_engine = core_systems["tool_engine"]
        
        return {
            "status": "operational",
            "active_sessions": len(active_sessions),
            "websocket_connections": len(websocket_connections),
            "knowledge_base": {
                "total_notes": len(link_engine.note_metadata),
                "total_links": sum(len(analysis.outgoing_links) for analysis in link_engine.link_analyses.values()),
            },
            "context_manager": context_manager.get_enhanced_context_summary(),
            "tool_engine": tool_engine.get_execution_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }