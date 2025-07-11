"""
ArcanAgent Backend Main Entry Point
FastAPI application with MCP server integration
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.settings import settings
from backend.mcp.server import MCPServer
from backend.api.middleware import setup_middleware
from backend.api.v1 import cognitive, knowledge, learning, agents, sessions
from backend.database.connection import init_database


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting ArcanAgent Backend...")
    
    # Initialize database
    await init_database()
    
    # Start MCP server
    mcp_server = MCPServer(host=settings.MCP_SERVER_HOST, port=settings.MCP_SERVER_PORT)
    asyncio.create_task(mcp_server.start())
    
    logger.info("ArcanAgent Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ArcanAgent Backend...")
    await mcp_server.stop()


# Create FastAPI app
app = FastAPI(
    title="ArcanAgent Backend",
    description="MCP-based Agent system with GRAG knowledge graph",
    version="0.1.0",
    lifespan=lifespan,
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup middleware
setup_middleware(app)

# Include API routes
app.include_router(cognitive.router, prefix="/api/v1/cognitive", tags=["cognitive"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["learning"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(sessions.router, prefix="/api/v1/sessions", tags=["sessions"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "ArcanAgent Backend API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "ArcanAgent Backend is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )