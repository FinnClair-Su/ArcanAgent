"""
ArcanAgent FastAPI Server

Main FastAPI application setup inspired by NagaAgent's architecture.
Provides RESTful API endpoints and WebSocket support for the ArcanAgent system.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import config


# Configure logging
logger = logging.getLogger("ArcanAgent.Server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🔮 ArcanAgent server starting up...")
    
    # Initialize core systems here
    try:
        # Initialize knowledge base
        from .knowledge.note_manager import NoteManager
        from .core.bidirectional_links import BidirectionalLinkEngine
        
        # Store in app state for access by routes
        app.state.note_manager = NoteManager(config.system.knowledge_base_path)
        app.state.link_engine = BidirectionalLinkEngine(config.system.knowledge_base_path)
        
        logger.info("✅ Core systems initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize core systems: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔮 ArcanAgent server shutting down...")
    
    # Cleanup here if needed
    if hasattr(app.state, 'link_engine'):
        # Save any pending data
        logger.info("💾 Saving link index...")
    
    logger.info("✅ Shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    
    # Create FastAPI app with configuration
    app = FastAPI(
        title="ArcanAgent API",
        description="Personal Knowledge Management & Learning System API",
        version=config.system.version,
        docs_url="/docs" if config.api.enable_docs else None,
        redoc_url="/redoc" if config.api.enable_docs else None,
        openapi_url="/openapi.json" if config.api.enable_docs else None,
        lifespan=lifespan
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Add routes
    setup_routes(app)
    
    # Add error handlers
    setup_error_handlers(app)
    
    return app


def setup_middleware(app: FastAPI):
    """Set up middleware for the FastAPI app."""
    
    # CORS middleware
    if config.api.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.api.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(f"✅ CORS enabled for origins: {config.api.cors_origins}")
    
    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request, call_next):
        """Log all HTTP requests."""
        import time
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.debug(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        return response


def setup_routes(app: FastAPI):
    """Set up API routes."""
    
    # Import route modules
    from .api.routes import learning, notes, graph, system
    
    # Include routers with prefixes
    app.include_router(
        system.router,
        prefix="/api/v1/system",
        tags=["system"]
    )
    
    app.include_router(
        learning.router,
        prefix="/api/v1/learning",
        tags=["learning"]
    )
    
    app.include_router(
        notes.router,
        prefix="/api/v1/notes",
        tags=["notes"]
    )
    
    app.include_router(
        graph.router,
        prefix="/api/v1/graph",
        tags=["graph"]
    )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with basic information."""
        return {
            "name": "ArcanAgent API",
            "version": config.system.version,
            "description": "Personal Knowledge Management & Learning System",
            "docs_url": "/docs" if config.api.enable_docs else None,
            "philosophy": "Bidirectional Linking is All You Need 🔗"
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            # Check if knowledge base is accessible
            kb_path = Path(config.system.knowledge_base_path)
            kb_accessible = kb_path.exists() and kb_path.is_dir()
            
            # Check LLM configuration
            llm_configured = False
            if config.llm.default_provider == "openai":
                llm_configured = bool(
                    config.llm.openai.api_key and 
                    not config.llm.openai.api_key.startswith("sk-your-")
                )
            elif config.llm.default_provider == "anthropic":
                llm_configured = bool(
                    config.llm.anthropic.api_key and 
                    not config.llm.anthropic.api_key.startswith("sk-ant-your-")
                )
            
            status = "healthy" if (kb_accessible and llm_configured) else "degraded"
            
            return {
                "status": status,
                "version": config.system.version,
                "checks": {
                    "knowledge_base": "ok" if kb_accessible else "error",
                    "llm_config": "ok" if llm_configured else "error"
                },
                "timestamp": "2024-01-01T00:00:00Z"  # Will be replaced with actual timestamp
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            )
    
    logger.info("✅ API routes configured")


def setup_error_handlers(app: FastAPI):
    """Set up global error handlers."""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        """Handle HTTP exceptions."""
        logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error" if not config.system.debug else str(exc),
                "status_code": 500,
                "path": str(request.url.path)
            }
        )
    
    logger.info("✅ Error handlers configured")


# For development/testing
if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        log_level=config.system.log_level.lower(),
        reload=config.system.debug
    )