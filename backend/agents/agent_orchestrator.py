"""
ArcanAgent Orchestrator

Orchestrates the five Arcana agents in a complete learning pipeline:
1. 🔮 The High Priestess - Knowledge assessment
2. 🏮 The Hermit - Learning path planning  
3. ✨ The Magician - Content generation
4. ⚖️ Justice - Understanding evaluation
5. 🌸 The Empress - Memory consolidation

This creates a complete learning experience that transforms user queries
into lasting knowledge through the power of bidirectional linking.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from .base_agent import BaseAgent, AgentCapability, AgentResponse
from .the_high_priestess import TheHighPriestess
from .the_hermit import TheHermit
from .the_magician import TheMagician
from .justice import Justice
from .the_empress import TheEmpress

from backend.core.context_manager import ContextManager, ContextPriority
from backend.core.tool_call_engine import ToolCallEngine
from backend.core.llm_client import BaseLLMClient, get_llm_client
from backend.core.bidirectional_links import BidirectionalLinkEngine

logger = logging.getLogger("ArcanAgent.Orchestrator")


@dataclass
class OrchestrationResult:
    """Result of running the complete agent pipeline."""
    success: bool
    user_query: str
    total_execution_time: float
    agent_responses: Dict[str, AgentResponse] = field(default_factory=dict)
    pipeline_metadata: Dict[str, Any] = field(default_factory=dict)
    final_content: str = ""
    consolidated_links: set = field(default_factory=set)
    errors: List[str] = field(default_factory=list)


class ArcanaAgentOrchestrator:
    """
    Orchestrates the five Arcana agents in a complete learning pipeline.
    
    The orchestrator manages the flow of information between agents,
    ensuring each agent receives the context it needs from previous
    agents while maintaining the integrity of the learning process.
    """
    
    def __init__(
        self,
        link_engine: BidirectionalLinkEngine,
        context_manager: ContextManager,
        tool_engine: ToolCallEngine,
        llm_client: Optional[BaseLLMClient] = None
    ):
        """Initialize the orchestrator with core systems."""
        self.link_engine = link_engine
        self.context_manager = context_manager
        self.tool_engine = tool_engine
        self.llm_client = llm_client or get_llm_client()
        
        # Initialize the five Arcana agents
        self.agents = {
            "the_high_priestess": TheHighPriestess(
                link_engine=link_engine,
                context_manager=context_manager,
                tool_engine=tool_engine
            ),
            "the_hermit": TheHermit(
                link_engine=link_engine,
                context_manager=context_manager,
                tool_engine=tool_engine
            ),
            "the_magician": TheMagician(
                link_engine=link_engine,
                context_manager=context_manager,
                tool_engine=tool_engine
            ),
            "justice": Justice(
                link_engine=link_engine,
                context_manager=context_manager,
                tool_engine=tool_engine
            ),
            "the_empress": TheEmpress(
                link_engine=link_engine,
                context_manager=context_manager,
                tool_engine=tool_engine
            )
        }
        
        # Execution statistics
        self.total_orchestrations = 0
        self.successful_orchestrations = 0
        self.average_execution_time = 0.0
        
        logger.info("🎭 ArcanAgent Orchestrator initialized with 5 Arcana agents")
    
    async def orchestrate_learning(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResult:
        """
        Run the complete learning pipeline.
        
        Args:
            user_query: The user's learning request
            context: Optional additional context
            
        Returns:
            OrchestrationResult with complete learning session results
        """
        start_time = datetime.now()
        self.total_orchestrations += 1
        
        logger.info(f"🎭 Beginning orchestrated learning for: {user_query[:100]}...")
        
        try:
            # Initialize shared context
            shared_context = context.copy() if context else {}
            agent_responses = {}
            
            # Stage 1: Knowledge Assessment with The High Priestess 🔮
            logger.info("🔮 Stage 1: Knowledge Assessment")
            priestess_response = await self.agents["the_high_priestess"]._execute_with_monitoring(
                user_query, shared_context, self.llm_client
            )
            agent_responses["the_high_priestess"] = priestess_response
            
            if priestess_response.success:
                shared_context["high_priestess_assessment"] = priestess_response.metadata
                logger.info(f"🔮 Knowledge assessment completed with {priestess_response.confidence:.1%} confidence")
            else:
                logger.warning("🔮 Knowledge assessment failed, proceeding with limited context")
            
            # Stage 2: Learning Path Planning with The Hermit 🏮
            logger.info("🏮 Stage 2: Learning Path Planning")
            hermit_response = await self.agents["the_hermit"]._execute_with_monitoring(
                user_query, shared_context, self.llm_client
            )
            agent_responses["the_hermit"] = hermit_response
            
            if hermit_response.success:
                shared_context["hermit_plan"] = hermit_response.metadata
                logger.info(f"🏮 Learning path planned with {hermit_response.confidence:.1%} confidence")
            else:
                logger.warning("🏮 Learning path planning failed, proceeding with adaptive approach")
            
            # Stage 3: Content Generation with The Magician ✨
            logger.info("✨ Stage 3: Content Generation")
            magician_response = await self.agents["the_magician"]._execute_with_monitoring(
                user_query, shared_context, self.llm_client
            )
            agent_responses["the_magician"] = magician_response
            
            if magician_response.success:
                shared_context["magician_content"] = magician_response.metadata
                logger.info(f"✨ Content generated with {len(magician_response.links_discovered)} bidirectional links")
            else:
                logger.error("✨ Content generation failed - learning pipeline compromised")
                return self._create_error_result(user_query, start_time, agent_responses, "Content generation failed")
            
            # Stage 4: Understanding Evaluation with Justice ⚖️
            logger.info("⚖️ Stage 4: Understanding Evaluation")
            justice_response = await self.agents["justice"]._execute_with_monitoring(
                user_query, shared_context, self.llm_client
            )
            agent_responses["justice"] = justice_response
            
            if justice_response.success:
                shared_context["justice_evaluation"] = justice_response.metadata
                logger.info(f"⚖️ Understanding evaluated with {justice_response.confidence:.1%} confidence")
            else:
                logger.warning("⚖️ Understanding evaluation failed, proceeding to consolidation")
            
            # Stage 5: Memory Consolidation with The Empress 🌸
            logger.info("🌸 Stage 5: Memory Consolidation")
            empress_response = await self.agents["the_empress"]._execute_with_monitoring(
                user_query, shared_context, self.llm_client
            )
            agent_responses["the_empress"] = empress_response
            
            if empress_response.success:
                logger.info(f"🌸 Knowledge consolidated with {len(empress_response.links_discovered)} total links")
            else:
                logger.warning("🌸 Memory consolidation encountered issues")
            
            # Compile final results
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Determine overall success
            critical_agents_successful = (
                magician_response.success  # Content generation is critical
            )
            
            overall_success = critical_agents_successful
            if overall_success:
                self.successful_orchestrations += 1
            
            # Update average execution time
            self.average_execution_time = (
                (self.average_execution_time * (self.total_orchestrations - 1) + execution_time) 
                / self.total_orchestrations
            )
            
            # Create orchestration result
            result = OrchestrationResult(
                success=overall_success,
                user_query=user_query,
                total_execution_time=execution_time,
                agent_responses=agent_responses,
                pipeline_metadata=self._compile_pipeline_metadata(agent_responses),
                final_content=self._compile_final_content(agent_responses),
                consolidated_links=self._compile_consolidated_links(agent_responses)
            )
            
            logger.info(f"🎭 Orchestration completed in {execution_time:.2f}s with {'SUCCESS' if overall_success else 'PARTIAL SUCCESS'}")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"🎭 Orchestration failed: {e}")
            
            return OrchestrationResult(
                success=False,
                user_query=user_query,
                total_execution_time=execution_time,
                agent_responses=agent_responses,
                errors=[f"Orchestration error: {str(e)}"]
            )
    
    async def run_single_agent(
        self,
        agent_name: str,
        user_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Run a single agent for testing or specific needs.
        
        Args:
            agent_name: Name of the agent to run
            user_query: The user's query
            context: Optional context
            
        Returns:
            AgentResponse from the specified agent
        """
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}. Available: {list(self.agents.keys())}")
        
        agent = self.agents[agent_name]
        return await agent._execute_with_monitoring(user_query, context, self.llm_client)
    
    def _create_error_result(
        self,
        user_query: str,
        start_time: datetime,
        agent_responses: Dict[str, AgentResponse],
        error_message: str
    ) -> OrchestrationResult:
        """Create an error result."""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return OrchestrationResult(
            success=False,
            user_query=user_query,
            total_execution_time=execution_time,
            agent_responses=agent_responses,
            errors=[error_message]
        )
    
    def _compile_pipeline_metadata(self, agent_responses: Dict[str, AgentResponse]) -> Dict[str, Any]:
        """Compile metadata from all agent responses."""
        pipeline_metadata = {
            "agents_executed": len(agent_responses),
            "successful_agents": sum(1 for r in agent_responses.values() if r.success),
            "total_links_discovered": len(self._compile_consolidated_links(agent_responses)),
            "average_confidence": self._calculate_average_confidence(agent_responses),
            "execution_times": {
                name: response.execution_time 
                for name, response in agent_responses.items()
            }
        }
        
        # Add specific metadata from key agents
        if "the_high_priestess" in agent_responses:
            priestess_meta = agent_responses["the_high_priestess"].metadata
            pipeline_metadata["initial_mastery"] = priestess_meta.get("mastery_assessment", {}).get("overall_mastery", 0.0)
        
        if "justice" in agent_responses:
            justice_meta = agent_responses["justice"].metadata
            pipeline_metadata["final_comprehension"] = justice_meta.get("comprehension_score", {}).get("overall_score", 0.0)
        
        if "the_empress" in agent_responses:
            empress_meta = agent_responses["the_empress"].metadata
            pipeline_metadata["consolidation_quality"] = empress_meta.get("integration_results", {}).get("integration_score", 0.0)
        
        return pipeline_metadata
    
    def _compile_final_content(self, agent_responses: Dict[str, AgentResponse]) -> str:
        """Compile the final learning content."""
        final_content = "# 🎭 ArcanAgent Learning Session\n\n"
        
        # Add content from each successful agent
        agent_order = ["the_high_priestess", "the_hermit", "the_magician", "justice", "the_empress"]
        
        for agent_name in agent_order:
            if agent_name in agent_responses and agent_responses[agent_name].success:
                response = agent_responses[agent_name]
                final_content += f"{response.content}\n\n---\n\n"
        
        # Add summary
        final_content += "## 🎭 Learning Session Complete\n\n"
        final_content += f"The five Arcana agents have completed their work. "
        
        successful_count = sum(1 for r in agent_responses.values() if r.success)
        final_content += f"{successful_count}/5 agents completed successfully.\n\n"
        
        if successful_count >= 3:
            final_content += "Your learning journey has been enriched through the wisdom of the Arcana. "
            final_content += "The knowledge has been woven into your understanding through [[bidirectional links]], "
            final_content += "creating lasting connections that will serve you well in future learning.\n\n"
        
        final_content += "*The cards have spoken. Your knowledge grows ever deeper.*"
        
        return final_content
    
    def _compile_consolidated_links(self, agent_responses: Dict[str, AgentResponse]) -> set:
        """Compile all links discovered across agents."""
        all_links = set()
        
        for response in agent_responses.values():
            if response.success and response.links_discovered:
                all_links.update(response.links_discovered)
        
        return all_links
    
    def _calculate_average_confidence(self, agent_responses: Dict[str, AgentResponse]) -> float:
        """Calculate average confidence across successful agents."""
        successful_responses = [r for r in agent_responses.values() if r.success]
        if not successful_responses:
            return 0.0
        
        total_confidence = sum(r.confidence for r in successful_responses)
        return total_confidence / len(successful_responses)
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "total_orchestrations": self.total_orchestrations,
            "successful_orchestrations": self.successful_orchestrations,
            "success_rate": self.successful_orchestrations / max(1, self.total_orchestrations),
            "average_execution_time": self.average_execution_time,
            "agents_available": len(self.agents),
            "agent_stats": {
                name: agent.get_agent_stats() 
                for name, agent in self.agents.items()
            }
        }
    
    def get_agent_by_name(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name."""
        return self.agents.get(name)
    
    def list_available_agents(self) -> List[str]:
        """List all available agents."""
        return list(self.agents.keys())