"""
System Management API Routes

Provides system-level endpoints for health checks, configuration, and diagnostics.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ...config import config

router = APIRouter()
logger = logging.getLogger("ArcanAgent.API.System")


@router.get("/info")
async def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information.
    
    Returns:
        Dict containing system version, configuration, and status
    """
    return {
        "name": "ArcanAgent",
        "version": config.system.version,
        "description": "Personal Knowledge Management & Learning System",
        "philosophy": "Bidirectional Linking is All You Need 🔗",
        "knowledge_base_path": config.system.knowledge_base_path,
        "llm_provider": config.llm.default_provider,
        "debug_mode": config.system.debug
    }


@router.get("/config")
async def get_system_config() -> Dict[str, Any]:
    """
    Get sanitized system configuration.
    
    Returns:
        Dict containing non-sensitive configuration values
    """
    # Return sanitized config (exclude API keys and sensitive data)
    return {
        "system": {
            "version": config.system.version,
            "debug": config.system.debug,
            "log_level": config.system.log_level
        },
        "api": {
            "host": config.api.host,
            "port": config.api.port,
            "enable_docs": config.api.enable_docs
        },
        "learning": {
            "max_sessions": config.learning.max_sessions,
            "session_timeout_minutes": config.learning.session_timeout_minutes
        },
        "agents": {
            "max_tool_call_loops": config.agents.max_tool_call_loops,
            "enabled_agents": list(config.agents.arcana_agents.keys())
        }
    }


@router.post("/reload-config")
async def reload_config():
    """
    Reload system configuration from files.
    
    Note: This is a placeholder for future implementation.
    In production, this might require admin privileges.
    """
    # TODO: Implement configuration reloading
    logger.info("Configuration reload requested")
    raise HTTPException(
        status_code=501,
        detail="Configuration reloading not yet implemented"
    )