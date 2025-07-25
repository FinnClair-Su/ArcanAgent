"""
ArcanAgent Tarot-Inspired AI Agents

The five Arcana agents that form the core of ArcanAgent's learning system:
- 🔮 The High Priestess: Knowledge assessment and cognitive analysis
- 🏮 The Hermit: Learning path planning and ZPD identification  
- ✨ The Magician: Content generation and bidirectional linking
- ⚖️ Justice: Understanding evaluation and learning effectiveness
- 🌸 The Empress: Memory consolidation and knowledge integration
"""

from .base_agent import BaseAgent, AgentCapability, AgentResponse
from .the_high_priestess import TheHighPriestess
from .the_hermit import TheHermit
from .the_magician import TheMagician
from .justice import Justice
from .the_empress import TheEmpress
from .agent_orchestrator import ArcanaAgentOrchestrator, OrchestrationResult

__all__ = [
    "BaseAgent",
    "AgentCapability", 
    "AgentResponse",
    "TheHighPriestess",
    "TheHermit",
    "TheMagician",
    "Justice",
    "TheEmpress",
    "ArcanaAgentOrchestrator",
    "OrchestrationResult"
]