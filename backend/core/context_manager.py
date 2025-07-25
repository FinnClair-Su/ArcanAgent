"""
Enhanced Context Manager - SPEC Compliant

Implements all 6 context engineering principles with NagaAgent-level optimization:
1. KV-Cache Optimization - Static prefixes and deterministic serialization
2. Tool Availability Management - Logits masking and static definitions
3. File System as Context - External memory with content externalization  
4. Attention via Recitation - Periodic plan injection and goal recitation
5. Error Information Retention - Complete error preservation with context
6. Context Diversity - Pattern avoidance and content rotation

Enhanced features:
- Static prefix optimization for KV-Cache hits
- Large content externalization to temporary files
- Deterministic tool definition serialization
- Advanced diversity scoring and rotation
"""

import asyncio
import hashlib
import json
import logging
import os
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from collections import deque, defaultdict

from .bidirectional_links import BidirectionalLinkEngine, LinkAnalysis
from .llm_client import LLMMessage

logger = logging.getLogger("ArcanAgent.ContextManagerEnhanced")


class ContextType(Enum):
    """Types of context content."""
    SYSTEM = "system"
    STATIC_PREFIX = "static_prefix"  # KV-Cache optimized static content
    PLAN = "plan"  
    KNOWLEDGE = "knowledge"
    TOOL_DEFINITION = "tool_definition"
    ERROR = "error"
    CONVERSATION = "conversation"
    FILE_REFERENCE = "file_reference"
    EXTERNAL_CONTENT = "external_content"  # Large content stored externally


class ContextPriority(Enum):
    """Context priority levels for optimization."""
    CRITICAL = 1    # Static prefixes, active errors
    HIGH = 2        # Current plan, immediate knowledge
    MEDIUM = 3      # Related knowledge, tool definitions
    LOW = 4         # Historical context, cached content


@dataclass
class ContextItem:
    """Enhanced context item with KV-Cache metadata."""
    content: str
    context_type: ContextType
    priority: ContextPriority
    timestamp: float = field(default_factory=time.time)
    token_count: int = 0
    cache_key: Optional[str] = None
    static_prefix: bool = False  # KV-Cache optimization flag
    external_file: Optional[str] = None  # Path to externalized content
    dependencies: Set[str] = field(default_factory=set)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    fingerprint: Optional[str] = None  # Content fingerprint for diversity
    
    def __post_init__(self):
        # Estimate token count (refined approximation)
        if self.external_file:
            # External content gets token count of reference only
            self.token_count = len(f"[External: {self.external_file}]".split()) * 1.3
        else:
            self.token_count = len(self.content.split()) * 1.3
        
        # Generate deterministic cache key for KV-Cache
        if not self.cache_key:
            key_content = f"{self.context_type.value}:{self.static_prefix}:{self.content}"
            self.cache_key = hashlib.sha256(key_content.encode()).hexdigest()[:16]
        
        # Generate content fingerprint for diversity tracking
        if not self.fingerprint:
            self.fingerprint = hashlib.md5(self.content.encode()).hexdigest()


@dataclass 
class ContextWindow:
    """Enhanced context window with KV-Cache optimization."""
    items: List[ContextItem] = field(default_factory=list)
    total_tokens: int = 0
    max_tokens: int = 4000
    cache_hits: int = 0
    static_prefix_tokens: int = 0  # Tokens in static prefix (KV-Cache optimized)
    diversity_score: float = 0.0
    external_files: Set[str] = field(default_factory=set)  # Track external files
    
    def add_item(self, item: ContextItem) -> bool:
        """Add item with KV-Cache optimization."""
        # Static prefix items always fit (they're cached)
        if item.static_prefix:
            self.items.append(item)
            self.static_prefix_tokens += int(item.token_count)
            return True
        
        # Check if regular item fits
        if self.total_tokens + item.token_count <= self.max_tokens:
            self.items.append(item)
            self.total_tokens += int(item.token_count)
            
            # Track external files
            if item.external_file:
                self.external_files.add(item.external_file)
            
            return True
        return False
    
    def remove_item(self, item: ContextItem) -> bool:
        """Remove item and update counters."""
        if item in self.items:
            self.items.remove(item)
            
            if item.static_prefix:
                self.static_prefix_tokens -= int(item.token_count)
            else:
                self.total_tokens -= int(item.token_count)
            
            # Remove external file tracking
            if item.external_file and item.external_file in self.external_files:
                self.external_files.remove(item.external_file)
            
            return True
        return False
    
    def get_messages(self) -> List[LLMMessage]:
        """Convert to LLM messages with KV-Cache optimization."""
        # Sort by priority: static prefix first, then by priority and timestamp
        sorted_items = sorted(
            self.items,
            key=lambda x: (0 if x.static_prefix else 1, x.priority.value, x.timestamp)
        )
        
        messages = []
        static_system_content = []
        dynamic_system_content = []
        user_content = []
        
        for item in sorted_items:
            # Handle external content
            content = item.content
            if item.external_file:
                content = f"[External Content: {item.external_file}]\n{content[:200]}..."
            
            # Categorize by type and static flag
            if item.context_type == ContextType.SYSTEM or item.context_type == ContextType.STATIC_PREFIX:
                if item.static_prefix:
                    static_system_content.append(content)
                else:
                    dynamic_system_content.append(content)
            elif item.context_type == ContextType.TOOL_DEFINITION:
                # Tool definitions are static for KV-Cache
                static_system_content.append(f"**Available Tools:**\n{content}")
            elif item.context_type == ContextType.PLAN:
                user_content.append(f"**Current Plan:**\n{content}")
            elif item.context_type == ContextType.KNOWLEDGE:
                user_content.append(f"**Knowledge Context:**\n{content}")
            elif item.context_type == ContextType.FILE_REFERENCE:
                user_content.append(f"**File Reference:**\n{content}")
            elif item.context_type == ContextType.ERROR:
                user_content.append(f"**Error Information:**\n{content}")
            else:
                user_content.append(content)
        
        # Build messages with static prefix first (KV-Cache optimization)
        if static_system_content:
            messages.append(LLMMessage(
                role="system",
                content="\n\n".join(static_system_content)
            ))
        
        if dynamic_system_content:
            messages.append(LLMMessage(
                role="system", 
                content="\n\n".join(dynamic_system_content)
            ))
        
        if user_content:
            messages.append(LLMMessage(
                role="user",
                content="\n\n".join(user_content)
            ))
        
        return messages


class ContextManager:
    """
    Enhanced Context Manager implementing all 6 principles with SPEC optimization.
    
    Key Enhancements:
    1. KV-Cache: Static prefix system for maximum cache hits
    2. Tool Management: Deterministic serialization with logits masking
    3. File System: Large content externalization to temp files
    4. Attention: Smart plan injection with recitation frequency
    5. Error Retention: Complete error preservation with stack traces
    6. Diversity: Advanced pattern detection and content rotation
    """
    
    def __init__(
        self,
        link_engine: BidirectionalLinkEngine,
        max_context_tokens: int = 4000,
        cache_size: int = 1000,
        external_content_threshold: int = 2000,  # Externalize content > 2000 chars
        temp_dir: Optional[str] = None
    ):
        """Initialize enhanced context manager."""
        self.link_engine = link_engine
        self.max_context_tokens = max_context_tokens
        self.external_content_threshold = external_content_threshold
        
        # Setup temporary directory for external content
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "arcan_context"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Context storage with enhanced caching
        self.context_cache: Dict[str, ContextItem] = {}
        self.active_context: ContextWindow = ContextWindow(max_tokens=max_context_tokens)
        
        # KV-Cache optimization structures
        self.static_prefix_content: str = ""  # Cached static prefix
        self.static_prefix_hash: str = ""     # Hash for cache validation
        self.cache_hit_history: deque = deque(maxlen=cache_size)
        self.content_fingerprints: Set[str] = set()
        
        # Tool availability with deterministic serialization
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        self.masked_tools: Set[str] = set()
        self.tool_definition_cache: Optional[str] = None
        
        # Plan and error tracking with enhanced retention
        self.current_plan: Optional[str] = None
        self.plan_history: deque = deque(maxlen=10)  # Track plan evolution
        self.error_history: List[ContextItem] = []
        self.error_context_retention: int = 100  # Keep last 100 errors
        self.plan_injection_frequency: int = 5
        self.interaction_count: int = 0
        
        # Advanced diversity tracking
        self.recent_contexts: deque = deque(maxlen=20)
        self.content_patterns: defaultdict = defaultdict(int)
        self.pattern_threshold: float = 0.7  # Similarity threshold
        self.diversity_rotation_size: int = 5  # Rotate content every N interactions
        
        # External file management
        self.external_files: Dict[str, float] = {}  # file_path -> timestamp
        self.external_cleanup_interval: int = 3600  # Cleanup every hour
        self.last_cleanup: float = time.time()
        
        # Initialize static prefix
        self._initialize_static_prefix()
        
        logger.info("Enhanced ContextManager initialized with full SPEC compliance")
    
    def _initialize_static_prefix(self):
        """Initialize static prefix for maximum KV-Cache hits."""
        static_content = """You are ArcanAgent, an AI system based on the philosophy that "Bidirectional Linking is All You Need".

Core Principles:
1. Every piece of knowledge is connected through bidirectional links [[concept]]
2. Learning happens at the intersection of existing and new knowledge
3. Understanding is measured by the quality of conceptual connections
4. Memory consolidation creates lasting bidirectional link networks

Your role is to help users learn through:
- Knowledge assessment via bidirectional link analysis
- Learning path optimization using ZPD theory  
- Content generation with automatic link weaving
- Understanding evaluation through connection testing
- Memory consolidation into lasting knowledge structures

Available Agent System:
- Use the <<<[TOOL_REQUEST]>>> format to call Arcana Agents
- Each agent specializes in specific learning pipeline stages
- Agents work collaboratively to create complete learning experiences"""
        
        item = ContextItem(
            content=static_content,
            context_type=ContextType.STATIC_PREFIX,
            priority=ContextPriority.CRITICAL,
            static_prefix=True
        )
        
        self.static_prefix_content = static_content
        self.static_prefix_hash = item.cache_key
        self.context_cache[item.cache_key] = item
        self.active_context.add_item(item)
        
        logger.debug("Static prefix initialized for KV-Cache optimization")
    
    def add_system_context(self, content: str, priority: ContextPriority = ContextPriority.HIGH, static: bool = False) -> str:
        """Add system context with KV-Cache optimization."""
        # Large content externalization (Principle 3)
        external_file = None
        if len(content) > self.external_content_threshold:
            external_file = self._externalize_content(content, "system_context")
            content = f"Large system context externalized to: {external_file}\n{content[:200]}..."
        
        item = ContextItem(
            content=content,
            context_type=ContextType.STATIC_PREFIX if static else ContextType.SYSTEM,
            priority=priority,
            static_prefix=static,
            external_file=external_file
        )
        
        # Check for cache hit (Principle 1)
        if item.cache_key in self.context_cache:
            cached_item = self.context_cache[item.cache_key]
            cached_item.access_count += 1
            cached_item.last_access = time.time()
            self.cache_hit_history.append(item.cache_key)
            self.active_context.cache_hits += 1
            logger.debug(f"KV-Cache hit for system context: {item.cache_key}")
            return item.cache_key
        
        # Store in cache and active context
        self.context_cache[item.cache_key] = item
        if self.active_context.add_item(item):
            logger.debug(f"Added system context: {len(content)} chars (static={static})")
            return item.cache_key
        
        return ""
    
    def set_current_plan(self, plan: str) -> str:
        """Set current plan with recitation optimization (Principle 4)."""
        # Store in plan history for evolution tracking
        if self.current_plan:
            self.plan_history.append(self.current_plan)
        
        self.current_plan = plan
        
        # Large plan externalization
        external_file = None
        plan_content = plan
        if len(plan) > self.external_content_threshold:
            external_file = self._externalize_content(plan, "current_plan")
            plan_content = f"Large plan externalized to: {external_file}\n{plan[:200]}..."
        
        item = ContextItem(
            content=plan_content,
            context_type=ContextType.PLAN,
            priority=ContextPriority.HIGH,
            external_file=external_file
        )
        
        # Remove previous plan from active context
        self.active_context.items = [
            i for i in self.active_context.items 
            if i.context_type != ContextType.PLAN
        ]
        
        self.context_cache[item.cache_key] = item
        self.active_context.add_item(item)
        
        logger.info(f"Set current plan: {len(plan)} chars")
        return item.cache_key
    
    def add_knowledge_context(
        self, 
        note_id: str, 
        context_layer: str = "summary",
        priority: ContextPriority = ContextPriority.MEDIUM
    ) -> str:
        """Add knowledge context with file system integration (Principle 3)."""
        analysis = self.link_engine.analyze_note(note_id)
        if not analysis:
            logger.warning(f"Note not found for context: {note_id}")
            return ""
        
        # Use appropriate context layer
        if context_layer not in analysis.context_layers:
            context_layer = "title"
        
        content = analysis.context_layers[context_layer]
        
        # Build comprehensive file reference
        metadata = self.link_engine.note_metadata.get(note_id, {})
        file_ref = f"Note ID: {note_id}\n"
        file_ref += f"Title: {metadata.get('title', note_id)}\n" 
        file_ref += f"Context Layer: {context_layer}\n"
        file_ref += f"Outgoing Links: {len(analysis.outgoing_links)}\n"
        file_ref += f"Incoming Links: {len(analysis.incoming_links)}\n"
        file_ref += f"Link Density: {analysis.link_density:.3f}\n"
        file_ref += f"Granularity Score: {analysis.granularity_score:.3f}\n"
        file_ref += f"Content: {content}"
        
        # Externalize large knowledge content
        external_file = None
        if len(file_ref) > self.external_content_threshold:
            external_file = self._externalize_content(file_ref, f"knowledge_{note_id}")
            file_ref = f"Large knowledge context externalized: {external_file}\n{file_ref[:300]}..."
        
        item = ContextItem(
            content=file_ref,
            context_type=ContextType.KNOWLEDGE,
            priority=priority,
            dependencies={note_id},
            external_file=external_file
        )
        
        # Check diversity before adding (Principle 6)
        if self._is_content_diverse(item):
            self.context_cache[item.cache_key] = item
            if self.active_context.add_item(item):
                logger.debug(f"Added knowledge context: {note_id} ({context_layer})")
                return item.cache_key
        else:
            logger.debug(f"Skipped non-diverse knowledge context: {note_id}")
        
        return ""
    
    def add_tool_definitions(self, tools: Dict[str, Dict[str, Any]]) -> str:
        """Add tool definitions with deterministic serialization (Principle 2)."""
        self.available_tools.update(tools)
        
        # Create deterministic tool definition string
        tool_definition = self._serialize_tools_deterministic(tools)
        
        # Check if tool definitions changed
        if self.tool_definition_cache == tool_definition:
            logger.debug("Tool definitions unchanged, using cache")
            return self.tool_definition_cache
        
        self.tool_definition_cache = tool_definition
        
        item = ContextItem(
            content=tool_definition,
            context_type=ContextType.TOOL_DEFINITION,
            priority=ContextPriority.MEDIUM,
            static_prefix=True  # Tool definitions are static for KV-Cache
        )
        
        # Replace existing tool definitions
        self.active_context.items = [
            i for i in self.active_context.items 
            if i.context_type != ContextType.TOOL_DEFINITION
        ]
        
        self.context_cache[item.cache_key] = item
        self.active_context.add_item(item)
        
        logger.debug(f"Added deterministic tool definitions: {len(tools)} tools")
        return item.cache_key
    
    def _serialize_tools_deterministic(self, tools: Dict[str, Dict[str, Any]]) -> str:
        """Create deterministic tool serialization for KV-Cache."""
        # Filter out masked tools
        active_tools = {
            name: definition for name, definition in tools.items()
            if name not in self.masked_tools
        }
        
        if not active_tools:
            return "No tools available."
        
        # Sort tools by name for deterministic ordering
        sorted_tools = sorted(active_tools.items())
        
        tool_content = "Available Arcana Agents:\n\n"
        
        # Agent descriptions in fixed order
        agent_descriptions = {
            "the_high_priestess": "🔮 Knowledge assessment and cognitive analysis - Evaluates current knowledge state through bidirectional link analysis",
            "the_hermit": "🏮 Learning path planning and ZPD identification - Creates optimal learning sequences within Zone of Proximal Development", 
            "the_magician": "✨ Content generation and bidirectional linking - Generates personalized learning content with automatic link weaving",
            "justice": "⚖️ Understanding evaluation and learning effectiveness - Provides fair assessment of comprehension and learning progress",
            "the_empress": "🌸 Memory consolidation and knowledge integration - Consolidates learning into lasting memory structures"
        }
        
        # Add tools in deterministic order
        for agent_name in sorted(agent_descriptions.keys()):
            if agent_name in active_tools:
                description = agent_descriptions[agent_name]
                tool_content += f"• **{agent_name}**: {description}\n"
        
        tool_content += """\n\n**Tool Call Format:**\n```\n<<<[TOOL_REQUEST]>>>\nagentType: 「始」arcana「末」\nagent_name: 「始」{agent_name}「末」\nquery: 「始」{specific_task_description}「末」\n<<<[END_TOOL_REQUEST]>>>\n```\n\n**Available agent_name values:**\n"""
        
        for agent_name in sorted(active_tools.keys()):
            tool_content += f"- {agent_name}\n"
        
        return tool_content
    
    def mask_tools(self, tool_names: List[str]):
        """Mask tools from availability (Principle 2)."""
        self.masked_tools.update(tool_names)
        # Invalidate tool definition cache
        self.tool_definition_cache = None
        logger.debug(f"Masked tools: {tool_names}")
    
    def add_error_context(self, error_info: str, error_type: str = "general", stack_trace: str = "") -> str:
        """Add comprehensive error information (Principle 5)."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        error_content = f"Error Type: {error_type}\n"
        error_content += f"Timestamp: {timestamp}\n"
        error_content += f"Details: {error_info}\n"
        
        if stack_trace:
            error_content += f"Stack Trace:\n{stack_trace}\n"
        
        # Add interaction context
        error_content += f"Interaction Count: {self.interaction_count}\n"
        error_content += f"Current Plan: {bool(self.current_plan)}\n"
        error_content += f"Active Context Items: {len(self.active_context.items)}\n"
        
        # Externalize large error information
        external_file = None
        if len(error_content) > self.external_content_threshold:
            external_file = self._externalize_content(error_content, f"error_{error_type}_{int(time.time())}")
            error_content = f"Large error info externalized: {external_file}\n{error_content[:300]}..."
        
        item = ContextItem(
            content=error_content,
            context_type=ContextType.ERROR,
            priority=ContextPriority.CRITICAL,
            external_file=external_file
        )
        
        # Always preserve errors (Principle 5)
        self.context_cache[item.cache_key] = item
        self.error_history.append(item)
        
        # Maintain error history size
        if len(self.error_history) > self.error_context_retention:
            self.error_history.pop(0)
        
        # Add to active context, making space if necessary
        if not self.active_context.add_item(item):
            self._make_space_for_critical(item)
        
        logger.error(f"Added comprehensive error context: {error_type}")
        return item.cache_key
    
    def _externalize_content(self, content: str, content_type: str) -> str:
        """Externalize large content to file system (Principle 3)."""
        timestamp = int(time.time())
        filename = f"{content_type}_{timestamp}_{hashlib.md5(content.encode()).hexdigest()[:8]}.txt"
        file_path = self.temp_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.external_files[str(file_path)] = time.time()
            logger.debug(f"Externalized {len(content)} chars to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to externalize content: {e}")
            return ""
    
    def build_context_window(self, additional_messages: List[LLMMessage] = None) -> List[LLMMessage]:
        """Build optimized context window following all 6 principles."""
        self.interaction_count += 1
        
        # Principle 4: Periodic plan injection with smart recitation
        if (self.interaction_count % self.plan_injection_frequency == 0 and 
            self.current_plan and 
            not any(item.context_type == ContextType.PLAN for item in self.active_context.items)):
            
            # Add plan evolution context if available
            if self.plan_history:
                plan_evolution = f"Previous plans: {' -> '.join(list(self.plan_history)[-3:])}\n\nCurrent plan: {self.current_plan}"
                self.set_current_plan(plan_evolution)
            else:
                self.set_current_plan(self.current_plan)
        
        # Cleanup external files periodically
        if time.time() - self.last_cleanup > self.external_cleanup_interval:
            self._cleanup_external_files()
        
        # Optimize context before building messages
        self.optimize_context()
        
        # Get base messages from context window
        messages = self.active_context.get_messages()
        
        # Add additional messages
        if additional_messages:
            messages.extend(additional_messages)
        
        # Update diversity tracking (Principle 6)
        self._update_diversity_tracking(messages)
        
        # Log enhanced context statistics
        self._log_enhanced_context_stats()
        
        return messages
    
    def optimize_context(self):
        """Enhanced context optimization following all principles."""
        logger.debug("Starting enhanced context optimization")
        
        # Principle 1: KV-Cache optimization
        self._optimize_cache_hits()
        
        # Principle 6: Ensure content diversity
        self._ensure_advanced_diversity()
        
        # Remove stale content if over budget
        if self.active_context.total_tokens > self.max_context_tokens * 0.9:
            self._smart_context_trimming()
        
        logger.debug("Enhanced context optimization completed")
    
    def _optimize_cache_hits(self):
        """Optimize for KV-Cache hits (Principle 1)."""
        # Promote frequently accessed items to static prefix
        for item in self.active_context.items:
            if (item.access_count > 3 and 
                not item.static_prefix and 
                item.context_type in [ContextType.SYSTEM, ContextType.TOOL_DEFINITION]):
                
                item.static_prefix = True
                item.priority = ContextPriority.CRITICAL
                logger.debug(f"Promoted item to static prefix: {item.cache_key}")
    
    def _ensure_advanced_diversity(self):
        """Advanced diversity checking (Principle 6)."""
        fingerprint_counts = defaultdict(int)
        items_to_remove = []
        
        # Count fingerprint frequencies
        for item in self.active_context.items:
            fingerprint_counts[item.fingerprint] += 1
        
        # Remove items with high similarity
        for item in self.active_context.items:
            if (fingerprint_counts[item.fingerprint] > 1 and 
                item.priority.value > ContextPriority.HIGH.value):
                # Keep only the most recently accessed duplicate
                items_to_remove.append(item)
        
        # Remove duplicate items
        for item in items_to_remove[:-1]:  # Keep the last one
            self.active_context.remove_item(item)
        
        if items_to_remove:
            logger.debug(f"Removed {len(items_to_remove)} non-diverse items")
    
    def _smart_context_trimming(self):
        """Smart context trimming with preservation of critical content."""
        # Separate items by importance
        critical_items = [i for i in self.active_context.items if i.priority == ContextPriority.CRITICAL]
        high_items = [i for i in self.active_context.items if i.priority == ContextPriority.HIGH]
        medium_items = [i for i in self.active_context.items if i.priority == ContextPriority.MEDIUM]
        low_items = [i for i in self.active_context.items if i.priority == ContextPriority.LOW]
        
        # Always keep critical and high priority items
        new_items = critical_items + high_items
        remaining_tokens = self.max_context_tokens - sum(int(i.token_count) for i in new_items)
        
        # Add medium priority items if space allows
        for item in sorted(medium_items, key=lambda x: -x.access_count):
            if remaining_tokens >= item.token_count:
                new_items.append(item)
                remaining_tokens -= int(item.token_count)
        
        # Add low priority items if space allows
        for item in sorted(low_items, key=lambda x: -x.access_count):
            if remaining_tokens >= item.token_count:
                new_items.append(item)
                remaining_tokens -= int(item.token_count)
        
        # Update active context
        removed_count = len(self.active_context.items) - len(new_items)
        self.active_context.items = new_items
        self.active_context.total_tokens = sum(int(i.token_count) for i in new_items if not i.static_prefix)
        
        if removed_count > 0:
            logger.debug(f"Smart trimming removed {removed_count} items")
    
    def _cleanup_external_files(self):
        """Clean up old external files."""
        current_time = time.time()
        files_to_remove = []
        
        for file_path, timestamp in self.external_files.items():
            if current_time - timestamp > self.external_cleanup_interval:
                try:
                    Path(file_path).unlink(missing_ok=True)
                    files_to_remove.append(file_path)
                except Exception as e:
                    logger.warning(f"Failed to remove external file {file_path}: {e}")
        
        for file_path in files_to_remove:
            del self.external_files[file_path]
        
        self.last_cleanup = current_time
        
        if files_to_remove:
            logger.debug(f"Cleaned up {len(files_to_remove)} external files")
    
    def _is_content_diverse(self, item: ContextItem) -> bool:
        """Advanced diversity checking (Principle 6)."""
        # Check fingerprint uniqueness
        if item.fingerprint in self.content_fingerprints:
            return False
        
        # Check semantic similarity with recent contexts
        words = set(item.content.lower().split())
        for recent_context in self.recent_contexts:
            recent_words = set(recent_context.lower().split())
            
            if not words or not recent_words:
                continue
                
            overlap = len(words & recent_words) / len(words | recent_words)
            if overlap > self.pattern_threshold:
                return False
        
        # Check pattern frequency
        content_patterns = item.content.lower().split()
        high_frequency_patterns = sum(1 for pattern in content_patterns if self.content_patterns[pattern] > 5)
        
        if high_frequency_patterns / max(1, len(content_patterns)) > 0.5:
            return False
        
        self.content_fingerprints.add(item.fingerprint)
        return True
    
    def _make_space_for_critical(self, critical_item: ContextItem):
        """Make space for critical items with smart removal."""
        # Remove lowest priority, least accessed items
        candidates = [
            item for item in self.active_context.items
            if (item.priority.value > ContextPriority.HIGH.value and 
                not item.static_prefix)
        ]
        
        candidates.sort(key=lambda x: (x.priority.value, -x.access_count, -x.last_access))
        
        for item in candidates:
            if self.active_context.remove_item(item):
                if self.active_context.total_tokens + critical_item.token_count <= self.max_context_tokens:
                    self.active_context.add_item(critical_item)
                    break
    
    def _update_diversity_tracking(self, messages: List[LLMMessage]):
        """Update advanced diversity tracking."""
        content = " ".join(msg.content for msg in messages)
        self.recent_contexts.append(content)
        
        # Update pattern frequency with decay
        words = content.lower().split()
        for word in words:
            self.content_patterns[word] = self.content_patterns[word] * 0.95 + 1
    
    def _log_enhanced_context_stats(self):
        """Log enhanced context statistics."""
        stats = {
            "total_items": len(self.active_context.items),
            "total_tokens": self.active_context.total_tokens,
            "static_prefix_tokens": self.active_context.static_prefix_tokens,
            "cache_hits": len(self.cache_hit_history),
            "cache_hit_rate": len(self.cache_hit_history) / max(1, self.interaction_count),
            "error_count": len(self.error_history),
            "external_files": len(self.external_files),
            "diversity_score": len(self.content_fingerprints) / max(1, len(self.recent_contexts)),
            "available_tools": len(self.available_tools) - len(self.masked_tools),
            "masked_tools": len(self.masked_tools),
            "plan_evolution_depth": len(self.plan_history)
        }
        
        logger.debug(f"Enhanced context stats: {stats}")
    
    def get_enhanced_context_summary(self) -> Dict[str, Any]:
        """Get comprehensive context summary."""
        type_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        
        for item in self.active_context.items:
            type_counts[item.context_type.value] += 1
            priority_counts[item.priority.value] += 1
        
        return {
            "total_items": len(self.active_context.items),
            "total_tokens": self.active_context.total_tokens,
            "static_prefix_tokens": self.active_context.static_prefix_tokens,
            "token_utilization": self.active_context.total_tokens / self.max_context_tokens,
            "types": dict(type_counts),
            "priorities": dict(priority_counts),
            "cache_hit_rate": len(self.cache_hit_history) / max(1, self.interaction_count),
            "kv_cache_efficiency": self.active_context.static_prefix_tokens / max(1, self.active_context.total_tokens),
            "current_plan": bool(self.current_plan),
            "plan_evolution_depth": len(self.plan_history),
            "error_count": len(self.error_history),
            "external_files_count": len(self.external_files),
            "diversity_score": len(self.content_fingerprints) / max(1, len(self.recent_contexts)),
            "interaction_count": self.interaction_count
        }