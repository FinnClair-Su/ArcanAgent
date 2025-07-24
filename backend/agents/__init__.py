"""
ArcanAgent Agent System

This package contains the Arcana Agent system:
- Base Agent: Common functionality for all agents
- Agent Manager: Simplified management for the 5 fixed Arcana agents
- Arcana Agents: The five specialized learning agents
- Prompts: Agent prompt templates and management
"""

from .base_agent import BaseAgent
from .agent_manager import ArcanaAgentManager

__all__ = [
    "BaseAgent",
    "ArcanaAgentManager"
]