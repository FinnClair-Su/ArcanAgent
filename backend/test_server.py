#!/usr/bin/env python3
"""
Simple FastAPI server test for ArcanAgent.
Tests the basic server structure without full LLM and agent initialization.
"""

import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ArcanAgent.TestServer")

def create_test_app() -> FastAPI:
    """Create a test FastAPI application with basic routes."""
    
    app = FastAPI(
        title="ArcanAgent API - Test Mode",
        description="Personal Knowledge Management & Learning System API (Test Mode)",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Basic routes for testing
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "ArcanAgent API - Test Mode",
            "version": "0.1.0",
            "description": "Personal Knowledge Management & Learning System",
            "philosophy": "Bidirectional Linking is All You Need 🔗",
            "mode": "test"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "0.1.0",
            "mode": "test",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    # Test learning endpoints
    @app.post("/api/v1/learning/assess-knowledge")
    async def test_assess_knowledge():
        """Test knowledge assessment endpoint."""
        return {
            "success": True,
            "session_id": "test-session-123",
            "agent_name": "the_high_priestess",
            "content": "Test knowledge assessment response",
            "metadata": {"test": True},
            "confidence": 0.8,
            "execution_time": 1.2,
            "links_discovered": ["test-link-1", "test-link-2"],
            "errors": []
        }
    
    @app.post("/api/v1/learning/orchestrate")
    async def test_orchestrate():
        """Test complete learning orchestration endpoint."""
        return {
            "success": True,
            "session_id": "test-session-123",
            "total_execution_time": 5.5,
            "agents_executed": 5,
            "final_content": "Test orchestration complete",
            "consolidated_links": ["link-1", "link-2", "link-3"],
            "metadata": {"test_mode": True},
            "errors": []
        }
    
    @app.get("/api/v1/learning/status")
    async def test_learning_status():
        """Test learning system status endpoint."""
        return {
            "status": "operational",
            "active_sessions": 0,
            "websocket_connections": 0,
            "knowledge_base": {
                "total_notes": 0,
                "total_links": 0,
            },
            "context_manager": {"test": True},
            "tool_engine": {"test": True},
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    logger.info("✅ Test FastAPI server created successfully!")
    return app

if __name__ == "__main__":
    import uvicorn
    
    app = create_test_app()
    
    print("🔮 Starting ArcanAgent Test Server...")
    print("📚 API Documentation: http://127.0.0.1:8000/docs")
    print("🔗 Philosophy: Bidirectional Linking is All You Need")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=True
    )