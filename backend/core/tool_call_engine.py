"""
NagaAgent-Style Tool Call Engine

Implements the exact SPEC format for tool calling as required:
<<<[TOOL_REQUEST]>>>
agentType: 「始」arcana「末」
agent_name: 「始」{agent_name}「末」
query: 「始」{specific_task}「末」
<<<[END_TOOL_REQUEST]>>>

This engine supports recursive tool calling loops with the Arcana Agent system.
Key Features:
- SPEC-compliant tool request parsing
- Recursive tool calling with depth limits  
- Arcana Agent system integration
- Tool result integration into context
- Error handling and recovery
"""

import asyncio
import json
import logging
import re
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

from .context_manager import ContextManager, ContextPriority
from .llm_client import BaseLLMClient, LLMMessage, get_llm_client

logger = logging.getLogger("ArcanAgent.ToolCallEngine")


class ToolCallStatus(Enum):
    """Status of tool call execution."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class ToolCall:
    """Arcana Agent tool call with SPEC format."""
    agent_type: str = "arcana"
    agent_name: str = ""
    query: str = ""
    call_id: str = ""
    status: ToolCallStatus = ToolCallStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    execution_time: Optional[float] = None
    
    def __post_init__(self):
        if not self.call_id:
            self.call_id = f"{self.agent_name}_{int(self.start_time * 1000)}"
    
    def mark_success(self, result: Any):
        """Mark tool call as successful."""
        self.status = ToolCallStatus.SUCCESS
        self.result = result
        self.end_time = time.time()
        self.execution_time = self.end_time - self.start_time
    
    def mark_error(self, error: str):
        """Mark tool call as failed."""
        self.status = ToolCallStatus.ERROR
        self.error = error
        self.end_time = time.time()
        self.execution_time = self.end_time - self.start_time


class ToolCallEngine:
    """
    NagaAgent-style tool call engine implementing SPEC requirements.
    
    Key Features:
    - SPEC-compliant <<<[TOOL_REQUEST]>>> format parsing
    - Recursive tool calling loops up to max_recursion depth
    - Automatic tool result integration into LLM messages
    - Support for Arcana Agent system integration
    """
    
    def __init__(
        self,
        context_manager: ContextManager,
        max_recursion: int = 5,
        call_timeout: int = 60
    ):
        """Initialize the NagaAgent-style tool call engine."""
        self.context_manager = context_manager
        self.max_recursion = max_recursion
        self.call_timeout = call_timeout
        
        # Arcana Agent registry
        self.arcana_agents: Dict[str, Any] = {}
        
        # Execution tracking
        self.call_history: List[ToolCall] = []
        self.active_calls: Dict[str, ToolCall] = {}
        
        # Statistics
        self.total_calls: int = 0
        self.successful_calls: int = 0
        self.failed_calls: int = 0
        
        logger.info("ToolCallEngine initialized with SPEC compliance")
    
    def register_arcana_agent(self, agent_name: str, agent_instance: Any):
        """Register an Arcana Agent for tool calling."""
        self.arcana_agents[agent_name] = agent_instance
        logger.info(f"Registered Arcana Agent: {agent_name}")
    
    def get_arcana_tool_definitions(self) -> str:
        """Get Arcana Agent tool definitions in SPEC format."""
        if not self.arcana_agents:
            return "No Arcana Agents available."
        
        tool_definitions = "Available Arcana Agents:\n\n"
        
        agent_descriptions = {
            "the_high_priestess": "🔮 Knowledge assessment and cognitive analysis - Evaluates current knowledge state through bidirectional link analysis",
            "the_hermit": "🏮 Learning path planning and ZPD identification - Creates optimal learning sequences within Zone of Proximal Development", 
            "the_magician": "✨ Content generation and bidirectional linking - Generates personalized learning content with automatic link weaving",
            "justice": "⚖️ Understanding evaluation and learning effectiveness - Provides fair assessment of comprehension and learning progress",
            "the_empress": "🌸 Memory consolidation and knowledge integration - Consolidates learning into lasting memory structures"
        }
        
        for agent_name in sorted(self.arcana_agents.keys()):
            description = agent_descriptions.get(agent_name, f"Arcana Agent: {agent_name}")
            tool_definitions += f"• **{agent_name}**: {description}\n"
        
        tool_definitions += """\n\n**Tool Call Format:**\n```\n<<<[TOOL_REQUEST]>>>\nagentType: 「始」arcana「末」\nagent_name: 「始」{agent_name}「末」\nquery: 「始」{specific_task_description}「末」\n<<<[END_TOOL_REQUEST]>>>\n```\n\n**Available agent_name values:**\n"""
        
        for agent_name in sorted(self.arcana_agents.keys()):
            tool_definitions += f"- {agent_name}\n"
        
        return tool_definitions
    
    async def handle_tool_call_loop(
        self,
        messages: List[LLMMessage],
        llm_client: Optional[BaseLLMClient] = None,
        max_recursion: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Handle the complete tool call loop as per SPEC.
        
        This is the main entry point that implements NagaAgent's recursive
        tool calling mechanism with SPEC-compliant format parsing.
        """
        if llm_client is None:
            llm_client = get_llm_client()
        
        if max_recursion is None:
            max_recursion = self.max_recursion
        
        logger.info(f"Starting tool call loop (max_recursion={max_recursion})")
        
        # Initialize execution context
        recursion_depth = 0
        current_messages = messages.copy()
        tool_calls_made = []
        
        # Add Arcana Agent definitions to context
        tool_definitions = self.get_arcana_tool_definitions()
        self.context_manager.add_system_context(
            f"Available Tools:\n{tool_definitions}",
            ContextPriority.HIGH
        )
        
        try:
            while recursion_depth < max_recursion:
                logger.debug(f"Tool call loop iteration {recursion_depth + 1}/{max_recursion}")
                
                # Build context window with current state
                context_messages = self.context_manager.build_context_window(current_messages)
                
                # Call LLM
                async with llm_client:
                    llm_response = await llm_client.chat_completion(context_messages)
                
                # Parse tool requests from response
                tool_calls = self._parse_tool_requests(llm_response.content)
                
                if not tool_calls:
                    # No tool calls found, return final response
                    logger.info(f"No tool calls found, returning final response after {recursion_depth} iterations")
                    return {
                        "content": llm_response.content,
                        "recursion_depth": recursion_depth,
                        "tool_calls_made": tool_calls_made,
                        "success": True
                    }
                
                # Execute tool calls
                tool_results = await self._execute_arcana_tool_calls(tool_calls)
                tool_calls_made.extend(tool_calls)
                
                # Add LLM response and tool results to message history
                current_messages.append(LLMMessage(
                    role="assistant",
                    content=llm_response.content
                ))
                
                # Format tool results for next iteration
                tool_results_content = self._format_tool_results(tool_results)
                current_messages.append(LLMMessage(
                    role="user", 
                    content=tool_results_content
                ))
                
                recursion_depth += 1
            
            # Max recursion reached
            logger.warning(f"Max recursion depth {max_recursion} reached")
            
            # Try to get final response
            final_messages = current_messages + [LLMMessage(
                role="user",
                content="Please provide a final response based on the tool execution results above. Do not make any more tool calls."
            )]
            
            context_messages = self.context_manager.build_context_window(final_messages)
            async with llm_client:
                final_response = await llm_client.chat_completion(context_messages)
            
            return {
                "content": final_response.content,
                "recursion_depth": recursion_depth,
                "tool_calls_made": tool_calls_made,
                "success": True,
                "max_recursion_reached": True
            }
            
        except Exception as e:
            error_msg = f"Tool call loop failed: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            self.context_manager.add_error_context(
                f"{error_msg}\n{traceback.format_exc()}",
                "tool_call_loop"
            )
            
            return {
                "content": f"Tool execution encountered an error: {error_msg}",
                "recursion_depth": recursion_depth,
                "tool_calls_made": tool_calls_made,
                "success": False,
                "error": error_msg
            }
    
    def _parse_tool_requests(self, content: str) -> List[ToolCall]:
        """
        Parse SPEC-compliant tool requests from LLM response.
        
        Expected format:
        <<<[TOOL_REQUEST]>>>
        agentType: 「始」arcana「末」
        agent_name: 「始」the_high_priestess「末」
        query: 「始」评估用户当前知识状态「末」
        <<<[END_TOOL_REQUEST]>>>
        """
        tool_calls = []
        
        # Find all tool request blocks
        pattern = r'<<<\[TOOL_REQUEST\]>>>(.*?)<<<\[END_TOOL_REQUEST\]>>>'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                # Parse each field
                agent_type_match = re.search(r'agentType:\s*「始」(.+?)「末」', match.strip())
                agent_name_match = re.search(r'agent_name:\s*「始」(.+?)「末」', match.strip())
                query_match = re.search(r'query:\s*「始」(.+?)「末」', match.strip(), re.DOTALL)
                
                if not all([agent_type_match, agent_name_match, query_match]):
                    logger.warning(f"Incomplete tool request format: {match.strip()}")
                    continue
                
                agent_type = agent_type_match.group(1).strip()
                agent_name = agent_name_match.group(1).strip()
                query = query_match.group(1).strip()
                
                # Validate agent type
                if agent_type != "arcana":
                    logger.warning(f"Invalid agent type: {agent_type} (expected: arcana)")
                    continue
                
                # Validate agent name
                if agent_name not in self.arcana_agents:
                    logger.warning(f"Unknown Arcana Agent: {agent_name}")
                    continue
                
                # Create tool call
                tool_call = ToolCall(
                    agent_type=agent_type,
                    agent_name=agent_name,
                    query=query
                )
                
                tool_calls.append(tool_call)
                logger.info(f"Parsed tool call: {agent_name} - {query[:50]}...")
                
            except Exception as e:
                logger.error(f"Failed to parse tool request: {e}\nContent: {match}")
                continue
        
        return tool_calls
    
    async def _execute_arcana_tool_calls(self, tool_calls: List[ToolCall]) -> List[ToolCall]:
        """Execute Arcana Agent tool calls."""
        logger.info(f"Executing {len(tool_calls)} Arcana tool calls")
        
        executed_calls = []
        
        for tool_call in tool_calls:
            logger.info(f"Executing {tool_call.agent_name}: {tool_call.query[:100]}...")
            
            tool_call.status = ToolCallStatus.RUNNING
            self.active_calls[tool_call.call_id] = tool_call
            self.total_calls += 1
            
            try:
                # Get agent instance
                agent = self.arcana_agents[tool_call.agent_name]
                
                # Execute agent with timeout
                result = await asyncio.wait_for(
                    agent._execute_with_monitoring(
                        user_query=tool_call.query,
                        context=None,  # Could pass shared context here
                        llm_client=None  # Agent will use default
                    ),
                    timeout=self.call_timeout
                )
                
                tool_call.mark_success(result)
                self.successful_calls += 1
                
                logger.info(f"Tool call successful: {tool_call.agent_name} ({tool_call.execution_time:.2f}s)")
                
            except asyncio.TimeoutError:
                error_msg = f"Tool call timeout: {tool_call.agent_name}"
                tool_call.mark_error(error_msg)
                self.failed_calls += 1
                logger.error(error_msg)
                
            except Exception as e:
                error_msg = f"Tool call error: {tool_call.agent_name} - {str(e)}"
                tool_call.mark_error(error_msg)
                self.failed_calls += 1
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
            
            finally:
                # Remove from active calls and add to history
                if tool_call.call_id in self.active_calls:
                    del self.active_calls[tool_call.call_id]
                self.call_history.append(tool_call)
                executed_calls.append(tool_call)
        
        return executed_calls
    
    async def execute_tool_calls(
        self,
        tool_calls: List[ToolCall],
        context: Optional[Dict[str, Any]] = None,
        parallel: bool = False
    ) -> List[ToolCall]:
        """Execute multiple tool calls (for backward compatibility)."""
        return await self._execute_arcana_tool_calls(tool_calls)
    
    def _format_tool_results(self, tool_calls: List[ToolCall]) -> str:
        """Format tool execution results for LLM context."""
        if not tool_calls:
            return "No tool calls were executed."
        
        results_content = "Tool Execution Results:\n\n"
        
        for tool_call in tool_calls:
            results_content += f"**{tool_call.agent_name.replace('_', ' ').title()}** ({tool_call.call_id}):\n"
            results_content += f"Query: {tool_call.query}\n"
            results_content += f"Status: {tool_call.status.value}\n"
            
            if tool_call.status == ToolCallStatus.SUCCESS:
                # Format agent response
                if hasattr(tool_call.result, 'content'):
                    # Limit content length to prevent context overflow
                    content = tool_call.result.content[:2000]
                    if len(tool_call.result.content) > 2000:
                        content += "\n\n[Content truncated for brevity...]"
                    results_content += f"Result:\n{content}\n"
                    
                    # Add metadata if available
                    if hasattr(tool_call.result, 'confidence'):
                        results_content += f"Confidence: {tool_call.result.confidence:.2%}\n"
                    
                    if hasattr(tool_call.result, 'links_discovered') and tool_call.result.links_discovered:
                        links_list = list(tool_call.result.links_discovered)[:5]  # Show first 5 links
                        results_content += f"Links Discovered: {', '.join(links_list)}\n"
                else:
                    results_content += f"Result: {str(tool_call.result)[:500]}...\n"
            else:
                results_content += f"Error: {tool_call.error}\n"
            
            results_content += f"Execution Time: {tool_call.execution_time:.2f}s\n"
            results_content += "\n---\n\n"
        
        return results_content
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": self.successful_calls / max(1, self.total_calls),
            "active_calls": len(self.active_calls),
            "registered_agents": len(self.arcana_agents),
            "call_history_size": len(self.call_history),
            "average_execution_time": sum(
                call.execution_time or 0 for call in self.call_history
            ) / max(1, len(self.call_history))
        }
    
    def clear_history(self):
        """Clear call history."""
        self.call_history.clear()
        logger.info("Tool call history cleared")
    
    def get_agent_names(self) -> List[str]:
        """Get list of registered agent names."""
        return list(self.arcana_agents.keys())


# Helper function to create and configure the engine
async def create_tool_engine(
    context_manager: ContextManager,
    arcana_agents: Dict[str, Any]
) -> ToolCallEngine:
    """Create and configure a SPEC-compliant tool call engine."""
    engine = ToolCallEngine(context_manager)
    
    # Register Arcana Agents
    for agent_name, agent_instance in arcana_agents.items():
        engine.register_arcana_agent(agent_name, agent_instance)
    
    logger.info(f"Created SPEC tool engine with {len(arcana_agents)} Arcana Agents")
    return engine