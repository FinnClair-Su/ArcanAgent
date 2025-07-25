"""
Base Agent for ArcanAgent System

Provides common functionality and interface for all Arcana agents.
Each agent embodies specific Tarot wisdom while following the core
principle that "Bidirectional Linking is All You Need".
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

from backend.core.context_manager import ContextManager, ContextPriority
from backend.core.tool_call_engine import ToolCallEngine, ToolCall
from backend.core.llm_client import BaseLLMClient, LLMMessage, get_llm_client
from backend.core.bidirectional_links import BidirectionalLinkEngine

logger = logging.getLogger("ArcanAgent.BaseAgent")


class AgentCapability(Enum):
    """Agent capabilities."""
    KNOWLEDGE_ASSESSMENT = "knowledge_assessment"
    PATH_PLANNING = "path_planning"
    CONTENT_GENERATION = "content_generation"
    UNDERSTANDING_EVALUATION = "understanding_evaluation"
    MEMORY_CONSOLIDATION = "memory_consolidation"
    LINK_ANALYSIS = "link_analysis"
    COGNITIVE_ANALYSIS = "cognitive_analysis"


@dataclass
class AgentResponse:
    """Standard response format from agents."""
    agent_name: str
    capability: AgentCapability
    success: bool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    reasoning: Optional[str] = None
    confidence: float = 0.0
    execution_time: float = 0.0
    tool_calls_made: List[str] = field(default_factory=list)
    links_discovered: Set[str] = field(default_factory=set)
    errors: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """
    Abstract base class for all Arcana agents.
    
    Each agent follows the same pattern:
    1. Analyze the current context using bidirectional links
    2. Use the tool call engine to gather information
    3. Apply its specific expertise and wisdom
    4. Return structured results for the next agent
    """
    
    def __init__(
        self,
        name: str,
        tarot_card: str,
        wisdom: str,
        primary_capability: AgentCapability,
        link_engine: BidirectionalLinkEngine,
        context_manager: ContextManager,
        tool_engine: ToolCallEngine
    ):
        """Initialize the base agent."""
        self.name = name
        self.tarot_card = tarot_card
        self.wisdom = wisdom
        self.primary_capability = primary_capability
        
        # Core systems
        self.link_engine = link_engine
        self.context_manager = context_manager
        self.tool_engine = tool_engine
        
        # Agent state
        self.session_memory: Dict[str, Any] = {}
        self.execution_history: List[AgentResponse] = []
        
        # Statistics
        self.total_executions = 0
        self.successful_executions = 0
        self.average_execution_time = 0.0
        
        logger.info(f"Initialized {self.tarot_card} - {self.name}")
    
    @abstractmethod
    async def execute(
        self, 
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        llm_client: Optional[BaseLLMClient] = None
    ) -> AgentResponse:
        """Execute the agent's primary function."""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the agent's system prompt."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Get the agent's capabilities."""
        pass
    
    async def _execute_with_monitoring(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        llm_client: Optional[BaseLLMClient] = None
    ) -> AgentResponse:
        """Execute with monitoring and error handling."""
        start_time = time.time()
        self.total_executions += 1
        
        # Use default LLM client if none provided
        if llm_client is None:
            llm_client = get_llm_client()
        
        try:
            # Set agent context
            self.context_manager.add_system_context(
                self.get_system_prompt(),
                ContextPriority.CRITICAL
            )
            
            # Add current session to context
            if context:
                self.session_memory.update(context)
            
            # Execute the agent
            response = await self.execute(user_query, context, llm_client)
            
            # Update statistics
            execution_time = time.time() - start_time
            response.execution_time = execution_time
            
            if response.success:
                self.successful_executions += 1
            
            # Update average execution time
            self.average_execution_time = (
                (self.average_execution_time * (self.total_executions - 1) + execution_time) 
                / self.total_executions
            )
            
            # Store in history
            self.execution_history.append(response)
            
            logger.info(f"{self.tarot_card} executed successfully in {execution_time:.2f}s")
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Agent execution failed: {str(e)}"
            
            # Create error response
            response = AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=False,
                content="",
                execution_time=execution_time,
                errors=[error_msg]
            )
            
            # Add error to context
            self.context_manager.add_error_context(
                f"{self.tarot_card} Error: {error_msg}",
                "agent_execution"
            )
            
            logger.error(f"{self.tarot_card} execution failed: {e}")
            return response
    
    async def _call_llm(
        self,
        messages: List[LLMMessage],
        llm_client: BaseLLMClient,
        temperature: float = 0.7
    ) -> str:
        """Call LLM with context management."""
        # Build complete context
        context_messages = self.context_manager.build_context_window(messages)
        
        # Make LLM call
        async with llm_client:
            response = await llm_client.chat_completion(context_messages)
        
        return response.content
    
    async def _use_tools(
        self,
        tool_calls: List[ToolCall],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """Use tools through the tool engine."""
        executed_calls = await self.tool_engine.execute_tool_calls(
            tool_calls, 
            context,
            parallel=True
        )
        
        # Extract results
        results = []
        for call in executed_calls:
            if call.status.name == "SUCCESS":
                results.append(call.result)
            else:
                results.append({"error": call.error})
        
        return results
    
    def _analyze_bidirectional_links(
        self,
        note_ids: List[str],
        depth: int = 2
    ) -> Dict[str, Any]:
        """Analyze bidirectional links for given notes."""
        analysis_results = {}
        
        for note_id in note_ids:
            # Get link analysis
            analysis = self.link_engine.analyze_note(note_id)
            if analysis:
                # Get neighborhood
                neighborhood = self.link_engine.get_note_neighborhood(note_id, depth)
                
                analysis_results[note_id] = {
                    "outgoing_links": list(analysis.outgoing_links),
                    "incoming_links": list(analysis.incoming_links),
                    "link_density": analysis.link_density,
                    "granularity_score": analysis.granularity_score,
                    "neighborhood": neighborhood,
                    "context_layers": analysis.context_layers
                }
        
        return analysis_results
    
    def _find_learning_paths(
        self,
        from_notes: List[str],
        to_notes: List[str],
        max_depth: int = 5
    ) -> Dict[str, Any]:
        """Find learning paths between note sets."""
        paths = {}
        
        for from_note in from_notes:
            for to_note in to_notes:
                path_info = self.link_engine.find_shortest_path(
                    from_note, 
                    to_note, 
                    max_depth
                )
                
                if path_info:
                    key = f"{from_note} -> {to_note}"
                    paths[key] = {
                        "path": path_info.path,
                        "distance": path_info.distance,
                        "cognitive_weight": path_info.cognitive_weight,
                        "learning_readiness": path_info.learning_readiness
                    }
        
        return paths
    
    def _extract_links_from_text(self, text: str) -> Set[str]:
        """Extract [[wiki-style]] links from text."""
        import re
        pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(pattern, text)
        
        links = set()
        for match in matches:
            # Handle links with aliases: [[target|alias]] -> target
            if '|' in match:
                target = match.split('|')[0].strip()
            else:
                target = match.strip()
            
            # Normalize to note ID format
            target = target.replace(' ', '_').lower()
            links.add(target)
        
        return links
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent execution statistics."""
        return {
            "agent_name": self.name,
            "tarot_card": self.tarot_card,
            "primary_capability": self.primary_capability.value,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "success_rate": self.successful_executions / max(1, self.total_executions),
            "average_execution_time": self.average_execution_time,
            "session_memory_size": len(self.session_memory),
            "execution_history_size": len(self.execution_history)
        }
    
    def clear_session_memory(self):
        """Clear session memory."""
        self.session_memory.clear()
        logger.info(f"{self.tarot_card} session memory cleared")
    
    def get_recent_responses(self, limit: int = 5) -> List[AgentResponse]:
        """Get recent agent responses."""
        return self.execution_history[-limit:] if self.execution_history else []