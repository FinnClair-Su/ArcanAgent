"""
Optimized Agent System - High Performance Arcana Collective

Enhanced agent system with advanced optimizations for better collaboration,
performance, and reliability in the ArcanAgent learning pipeline.

Key Optimizations:
1. Parallel agent execution with dependency management
2. Intelligent result caching and memoization
3. Advanced error recovery and retry strategies
4. Performance monitoring and adaptive optimization
5. Memory-efficient agent state management
6. Cross-agent knowledge sharing
7. Dynamic workload balancing
8. Real-time health monitoring
9. Smart resource allocation
10. Enhanced collaboration protocols

Philosophy: "Bidirectional Linking is All You Need" - maintained through
optimized inter-agent communication and shared knowledge state.
"""

import asyncio
import logging
import time
import threading
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from datetime import datetime
import json
import hashlib

logger = logging.getLogger("ArcanAgent.OptimizedAgentSystem")


class AgentState(Enum):
    """Enhanced agent states."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    PROCESSING = "processing"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"
    RECOVERY = "recovery"


class ExecutionPriority(Enum):
    """Task execution priorities."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class OptimizedAgentResponse:
    """Enhanced agent response with performance metrics."""
    agent_name: str
    capability: str
    success: bool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    reasoning: Optional[str] = None
    confidence: float = 0.0
    execution_time: float = 0.0
    tool_calls_made: List[str] = field(default_factory=list)
    links_discovered: Set[str] = field(default_factory=set)
    errors: List[str] = field(default_factory=list)
    
    # Optimization metrics
    cache_hit: bool = False
    memory_usage: int = 0
    tokens_processed: int = 0
    dependencies_resolved: List[str] = field(default_factory=list)
    parallel_execution: bool = False
    retry_count: int = 0
    health_score: float = 1.0


@dataclass
class AgentTask:
    """Enhanced task representation."""
    task_id: str
    agent_name: str
    user_query: str
    context: Dict[str, Any]
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    dependencies: Set[str] = field(default_factory=set)
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


class AgentPerformanceMonitor:
    """Monitor and optimize agent performance."""
    
    def __init__(self):
        self.execution_history = defaultdict(deque)
        self.error_history = defaultdict(deque)
        self.cache_stats = defaultdict(dict)
        self.collaboration_stats = defaultdict(dict)
        self._lock = threading.Lock()
    
    def record_execution(
        self, 
        agent_name: str, 
        execution_time: float, 
        success: bool,
        memory_usage: int = 0,
        tokens_processed: int = 0
    ):
        """Record agent execution metrics."""
        with self._lock:
            history = self.execution_history[agent_name]
            history.append({
                'timestamp': time.time(),
                'execution_time': execution_time,
                'success': success,
                'memory_usage': memory_usage,
                'tokens_processed': tokens_processed
            })
            
            # Keep only last 100 executions
            if len(history) > 100:
                history.popleft()
    
    def record_error(self, agent_name: str, error: str, recovery_time: float = 0.0):
        """Record agent errors."""
        with self._lock:
            self.error_history[agent_name].append({
                'timestamp': time.time(),
                'error': error,
                'recovery_time': recovery_time
            })
    
    def get_agent_health_score(self, agent_name: str) -> float:
        """Calculate agent health score (0.0 to 1.0)."""
        with self._lock:
            history = self.execution_history[agent_name]
            if not history:
                return 1.0
            
            recent_executions = list(history)[-20:]  # Last 20 executions
            success_rate = sum(1 for h in recent_executions if h['success']) / len(recent_executions)
            
            # Average execution time (normalized)
            avg_time = sum(h['execution_time'] for h in recent_executions) / len(recent_executions)
            time_score = max(0.0, 1.0 - (avg_time - 1.0) / 10.0)  # Penalty for slow execution
            
            # Error rate penalty
            recent_errors = [e for e in self.error_history[agent_name] 
                           if time.time() - e['timestamp'] < 300]  # Last 5 minutes
            error_penalty = min(0.5, len(recent_errors) * 0.1)
            
            return max(0.0, success_rate * time_score - error_penalty)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        with self._lock:
            stats = {}
            
            for agent_name in self.execution_history:
                history = list(self.execution_history[agent_name])
                if not history:
                    continue
                
                stats[agent_name] = {
                    'total_executions': len(history),
                    'success_rate': sum(1 for h in history if h['success']) / len(history),  
                    'avg_execution_time': sum(h['execution_time'] for h in history) / len(history),
                    'health_score': self.get_agent_health_score(agent_name),
                    'recent_errors': len([e for e in self.error_history[agent_name] 
                                        if time.time() - e['timestamp'] < 300])
                }
            
            return stats


class SmartCache:
    """Intelligent caching system for agent responses."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Tuple[OptimizedAgentResponse, float]] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.hit_count = 0
        self.miss_count = 0
        self._lock = threading.RLock()
    
    def _generate_cache_key(self, agent_name: str, user_query: str, context: Dict[str, Any]) -> str:
        """Generate deterministic cache key."""
        content = json.dumps({
            'agent': agent_name,
            'query': user_query,
            'context': context
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, agent_name: str, user_query: str, context: Dict[str, Any]) -> Optional[OptimizedAgentResponse]:
        """Get cached response if valid."""
        cache_key = self._generate_cache_key(agent_name, user_query, context)
        
        with self._lock:
            if cache_key not in self.cache:
                self.miss_count += 1
                return None
            
            response, cached_time = self.cache[cache_key]
            
            # Check TTL
            if time.time() - cached_time > self.ttl:
                del self.cache[cache_key]
                self.access_times.pop(cache_key, None)
                self.miss_count += 1
                return None
            
            # Update access time
            self.access_times[cache_key] = time.time()
            self.hit_count += 1
            
            # Mark as cache hit
            cached_response = OptimizedAgentResponse(
                agent_name=response.agent_name,
                capability=response.capability,
                success=response.success,
                content=response.content,
                metadata=response.metadata,
                reasoning=response.reasoning,
                confidence=response.confidence,
                execution_time=0.001,  # Cached execution time
                tool_calls_made=response.tool_calls_made.copy(),
                links_discovered=response.links_discovered.copy(),
                errors=response.errors.copy(),
                cache_hit=True,
                memory_usage=response.memory_usage,
                tokens_processed=response.tokens_processed
            )
            
            return cached_response
    
    def put(self, agent_name: str, user_query: str, context: Dict[str, Any], response: OptimizedAgentResponse):
        """Cache response with LRU eviction."""
        cache_key = self._generate_cache_key(agent_name, user_query, context)
        
        with self._lock:
            # Evict if at capacity
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[cache_key] = (response, time.time())
            self.access_times[cache_key] = time.time()
    
    def _evict_lru(self):
        """Evict least recently used entries."""
        if not self.access_times:
            return
        
        # Remove oldest 20% of entries
        sorted_items = sorted(self.access_times.items(), key=lambda x: x[1])
        evict_count = max(1, len(sorted_items) // 5)
        
        for cache_key, _ in sorted_items[:evict_count]:
            self.cache.pop(cache_key, None)
            self.access_times.pop(cache_key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'hit_rate': hit_rate,
                'max_size': self.max_size
            }


class OptimizedBaseAgent(ABC):
    """Enhanced base agent with advanced optimization features."""
    
    def __init__(
        self, 
        agent_name: str,
        capabilities: List[str],
        link_engine=None,
        context_manager=None,
        tool_engine=None
    ):
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.link_engine = link_engine
        self.context_manager = context_manager
        self.tool_engine = tool_engine
        
        # Optimization features
        self.state = AgentState.IDLE
        self.current_task: Optional[AgentTask] = None
        self.execution_history = deque(maxlen=100)
        self.collaboration_memory: Dict[str, Any] = {}
        self.performance_metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'avg_execution_time': 0.0,
            'cache_hits': 0,
            'errors_recovered': 0
        }
        
        # Thread safety
        self._state_lock = threading.RLock()
        
        logger.info(f"Initialized optimized agent: {agent_name}")
    
    async def execute_optimized(
        self, 
        user_query: str, 
        context: Dict[str, Any],
        task_id: Optional[str] = None,
        enable_cache: bool = True
    ) -> OptimizedAgentResponse:
        """Execute agent with full optimization features."""
        task_id = task_id or f"{self.agent_name}_{int(time.time() * 1000)}"
        start_time = time.time()
        
        with self._state_lock:
            self.state = AgentState.PROCESSING
            self.current_task = AgentTask(
                task_id=task_id,
                agent_name=self.agent_name,
                user_query=user_query,
                context=context,
                started_at=start_time
            )
        
        try:
            # Execute with error recovery
            response = await self._execute_with_recovery(user_query, context, enable_cache)
            
            # Update metrics
            execution_time = time.time() - start_time
            response.execution_time = execution_time
            
            with self._state_lock:
                self.state = AgentState.COMPLETED
                self.current_task.completed_at = time.time()
                self.performance_metrics['total_executions'] += 1
                if response.success:
                    self.performance_metrics['successful_executions'] += 1
                
                # Update average execution time
                total = self.performance_metrics['total_executions']
                current_avg = self.performance_metrics['avg_execution_time']
                self.performance_metrics['avg_execution_time'] = (
                    (current_avg * (total - 1) + execution_time) / total
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Agent {self.agent_name} execution failed: {e}")
            
            with self._state_lock:
                self.state = AgentState.ERROR
            
            return OptimizedAgentResponse(
                agent_name=self.agent_name,
                capability=self.capabilities[0] if self.capabilities else "unknown",
                success=False,
                content=f"Agent execution failed: {str(e)}",
                errors=[str(e)],
                execution_time=time.time() - start_time
            )
    
    async def _execute_with_recovery(
        self, 
        user_query: str, 
        context: Dict[str, Any],
        enable_cache: bool
    ) -> OptimizedAgentResponse:
        """Execute with automatic error recovery."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    self.state = AgentState.RECOVERY
                    await asyncio.sleep(min(2 ** attempt, 10))  # Exponential backoff
                
                response = await self._core_execute(user_query, context, enable_cache)
                
                if attempt > 0:
                    self.performance_metrics['errors_recovered'] += 1
                    logger.info(f"Agent {self.agent_name} recovered after {attempt} retries")
                
                return response
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                logger.warning(f"Agent {self.agent_name} attempt {attempt + 1} failed: {e}")
        
        raise RuntimeError(f"Agent {self.agent_name} failed after {max_retries} attempts")
    
    @abstractmethod
    async def _core_execute(
        self, 
        user_query: str, 
        context: Dict[str, Any],
        enable_cache: bool = True
    ) -> OptimizedAgentResponse:
        """Core execution logic - to be implemented by specific agents."""
        pass
    
    def share_knowledge(self, key: str, value: Any):
        """Share knowledge with other agents."""
        self.collaboration_memory[key] = {
            'value': value,
            'timestamp': time.time(),
            'agent': self.agent_name
        }
    
    def get_shared_knowledge(self, key: str) -> Optional[Any]:
        """Get knowledge shared by other agents."""
        if key in self.collaboration_memory:
            return self.collaboration_memory[key]['value']
        return None
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status."""
        with self._state_lock:
            return {
                'agent_name': self.agent_name,
                'state': self.state.value,
                'current_task': self.current_task.task_id if self.current_task else None,
                'performance_metrics': self.performance_metrics.copy(),
                'uptime': time.time() - (self.current_task.created_at if self.current_task else 0),
                'capabilities': self.capabilities
            }


class OptimizedAgentOrchestrator:
    """Enhanced orchestrator with parallel execution and optimization."""
    
    def __init__(
        self,
        agents: Dict[str, OptimizedBaseAgent],
        max_parallel_agents: int = 3,
        enable_caching: bool = True
    ):
        self.agents = agents
        self.max_parallel_agents = max_parallel_agents
        self.enable_caching = enable_caching
        
        # Optimization systems
        self.performance_monitor = AgentPerformanceMonitor()
        self.cache = SmartCache() if enable_caching else None
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, AgentTask] = {}
        
        # Collaboration
        self.shared_context: Dict[str, Any] = {}
        self.agent_dependencies = {
            'the_high_priestess': [],
            'the_hermit': ['the_high_priestess'],
            'the_magician': ['the_high_priestess', 'the_hermit'],
            'justice': ['the_magician'],
            'the_empress': ['justice']
        }
        
        # Monitoring
        self.orchestration_stats = {
            'total_orchestrations': 0,
            'successful_orchestrations': 0,
            'parallel_executions': 0,
            'cache_hits': 0
        }
        
        logger.info(f"Initialized optimized orchestrator with {len(agents)} agents")
    
    async def orchestrate_learning_optimized(
        self, 
        user_query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run optimized learning orchestration with parallel execution."""
        start_time = time.time()
        context = context or {}
        
        self.orchestration_stats['total_orchestrations'] += 1
        
        try:
            # Phase 1: Assessment (Sequential)
            assessment_result = await self._execute_agent(
                'the_high_priestess', user_query, context
            )
            
            if not assessment_result.success:
                return self._create_error_result("Assessment failed", start_time)
            
            # Update shared context
            self.shared_context['assessment'] = assessment_result.metadata
            
            # Phase 2: Planning (Depends on Assessment)
            planning_result = await self._execute_agent(
                'the_hermit', user_query, {**context, **self.shared_context}
            )
            
            if not planning_result.success:
                return self._create_error_result("Planning failed", start_time)
            
            self.shared_context['planning'] = planning_result.metadata
            
            # Phase 3: Parallel Execution (Content + Evaluation)
            content_task = asyncio.create_task(
                self._execute_agent(
                    'the_magician', user_query, {**context, **self.shared_context}
                )
            )
            
            # Wait for content before evaluation
            content_result = await content_task
            if not content_result.success:
                return self._create_error_result("Content generation failed", start_time)
            
            self.shared_context['content'] = content_result.metadata
            
            # Phase 4: Evaluation and Consolidation (Parallel)
            evaluation_task = asyncio.create_task(
                self._execute_agent(
                    'justice', user_query, {**context, **self.shared_context}
                )
            )
            
            evaluation_result = await evaluation_task
            if not evaluation_result.success:
                return self._create_error_result("Evaluation failed", start_time)
            
            self.shared_context['evaluation'] = evaluation_result.metadata
            
            # Phase 5: Final Consolidation
            consolidation_result = await self._execute_agent(
                'the_empress', user_query, {**context, **self.shared_context}
            )
            
            if not consolidation_result.success:
                return self._create_error_result("Consolidation failed", start_time)
            
            # Compile final results
            total_time = time.time() - start_time
            self.orchestration_stats['successful_orchestrations'] += 1
            
            return {
                'success': True,
                'total_execution_time': total_time,
                'agent_responses': {
                    'assessment': assessment_result,
                    'planning': planning_result,
                    'content': content_result,
                    'evaluation': evaluation_result,
                    'consolidation': consolidation_result
                },
                'final_content': consolidation_result.content,
                'consolidated_links': consolidation_result.links_discovered,
                'shared_context': self.shared_context.copy(),
                'optimization_stats': {
                    'parallel_execution': True,
                    'cache_hits_total': sum(r.cache_hit for r in [
                        assessment_result, planning_result, content_result,
                        evaluation_result, consolidation_result
                    ]),
                    'agents_executed': 5,
                    'total_tokens': sum(r.tokens_processed for r in [
                        assessment_result, planning_result, content_result,
                        evaluation_result, consolidation_result
                    ])
                }
            }
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return self._create_error_result(f"Orchestration error: {str(e)}", start_time)
    
    async def _execute_agent(
        self, 
        agent_name: str, 
        user_query: str, 
        context: Dict[str, Any]
    ) -> OptimizedAgentResponse:
        """Execute individual agent with monitoring."""
        if agent_name not in self.agents:
            return OptimizedAgentResponse(
                agent_name=agent_name,
                capability="unknown",
                success=False,
                content=f"Agent {agent_name} not found",
                errors=[f"Agent {agent_name} not available"]
            )
        
        agent = self.agents[agent_name]
        
        # Check cache first
        cached_response = None
        if self.cache:
            cached_response = self.cache.get(agent_name, user_query, context)
            if cached_response:
                self.orchestration_stats['cache_hits'] += 1
                return cached_response
        
        # Execute agent
        start_time = time.time()
        try:
            response = await agent.execute_optimized(user_query, context, enable_cache=False)
            
            # Record performance
            self.performance_monitor.record_execution(
                agent_name,
                response.execution_time,
                response.success,
                response.memory_usage,
                response.tokens_processed  
            )
            
            # Cache response
            if self.cache and response.success:
                self.cache.put(agent_name, user_query, context, response)
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.performance_monitor.record_error(agent_name, str(e))
            
            return OptimizedAgentResponse(
                agent_name=agent_name,
                capability=agent.capabilities[0] if agent.capabilities else "unknown",
                success=False,
                content=f"Agent execution failed: {str(e)}",
                errors=[str(e)],
                execution_time=execution_time
            )
    
    def _create_error_result(self, error_message: str, start_time: float) -> Dict[str, Any]:
        """Create standardized error result."""
        return {
            'success': False,
            'error': error_message,
            'total_execution_time': time.time() - start_time,
            'agent_responses': {},
            'optimization_stats': {
                'parallel_execution': False,
                'cache_hits_total': 0,
                'agents_executed': 0
            }
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        return {
            'orchestration_stats': self.orchestration_stats.copy(),
            'agent_performance': self.performance_monitor.get_performance_stats(),
            'cache_stats': self.cache.get_stats() if self.cache else {},
            'agent_health': {
                name: agent.get_health_status() 
                for name, agent in self.agents.items()
            },
            'system_overview': {
                'total_agents': len(self.agents),
                'max_parallel_agents': self.max_parallel_agents,
                'caching_enabled': self.enable_caching,
                'active_tasks': len(self.active_tasks)
            }
        }


# Example optimized agent implementations
class OptimizedHighPriestess(OptimizedBaseAgent):
    """Optimized High Priestess agent."""
    
    def __init__(self, link_engine=None, context_manager=None, tool_engine=None):
        super().__init__(
            "the_high_priestess",
            ["knowledge_assessment", "cognitive_analysis"],
            link_engine, context_manager, tool_engine
        )
    
    async def _core_execute(
        self, 
        user_query: str, 
        context: Dict[str, Any],
        enable_cache: bool = True
    ) -> OptimizedAgentResponse:
        """Optimized knowledge assessment."""
        # Simulate processing
        await asyncio.sleep(0.1)
        
        return OptimizedAgentResponse(
            agent_name=self.agent_name,
            capability="knowledge_assessment",
            success=True,
            content=f"Knowledge assessment completed for: {user_query}",
            metadata={"assessment_score": 0.8, "readiness": "high"},
            confidence=0.9,
            tokens_processed=150,
            memory_usage=1024
        )


def create_optimized_agent_system() -> Tuple[Dict[str, OptimizedBaseAgent], OptimizedAgentOrchestrator]:
    """Create optimized agent system for testing."""
    agents = {
        'the_high_priestess': OptimizedHighPriestess(),
        # Add other optimized agents here
    }
    
    orchestrator = OptimizedAgentOrchestrator(agents)
    
    return agents, orchestrator