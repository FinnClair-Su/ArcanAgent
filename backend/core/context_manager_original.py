"""
Context Manager

Implements the 6 core context engineering principles for optimal LLM performance:
1. KV-Cache Optimization - Maximize cache hit rates
2. Tool Availability Management - Static tool definitions with logits masking  
3. File System as Context - External memory through file references
4. Attention via Recitation - Periodic plan injection
5. Error Information Retention - Complete failure preservation
6. Context Diversity - Avoid pattern repetition

This manager provides intelligent context selection and optimization for ArcanAgent.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from collections import deque, defaultdict

from .bidirectional_links import BidirectionalLinkEngine, LinkAnalysis
from .llm_client import LLMMessage

logger = logging.getLogger("ArcanAgent.ContextManager")


class ContextType(Enum):
    """Types of context content."""
    SYSTEM = "system"
    PLAN = "plan"  
    KNOWLEDGE = "knowledge"
    TOOL_DEFINITION = "tool_definition"
    ERROR = "error"
    CONVERSATION = "conversation"
    FILE_REFERENCE = "file_reference"


class ContextPriority(Enum):
    """Context priority levels."""
    CRITICAL = 1    # System prompts, active errors
    HIGH = 2        # Current plan, immediate knowledge
    MEDIUM = 3      # Related knowledge, tool definitions
    LOW = 4         # Historical context, cached content


@dataclass
class ContextItem:
    """Individual context item with metadata."""
    content: str
    context_type: ContextType
    priority: ContextPriority
    timestamp: float = field(default_factory=time.time)
    token_count: int = 0
    cache_key: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    
    def __post_init__(self):
        # Estimate token count (rough approximation)
        self.token_count = len(self.content.split()) * 1.3  # ~1.3 tokens per word
        
        # Generate cache key for KV-cache optimization
        if not self.cache_key:
            self.cache_key = hashlib.md5(
                f"{self.context_type.value}:{self.content}".encode()
            ).hexdigest()[:16]


@dataclass 
class ContextWindow:
    """Context window with optimization metadata."""
    items: List[ContextItem] = field(default_factory=list)
    total_tokens: int = 0
    max_tokens: int = 4000
    cache_hits: int = 0
    diversity_score: float = 0.0
    
    def add_item(self, item: ContextItem) -> bool:
        """Add item if within token budget."""
        if self.total_tokens + item.token_count <= self.max_tokens:
            self.items.append(item)
            self.total_tokens += int(item.token_count)
            return True
        return False
    
    def remove_item(self, item: ContextItem) -> bool:
        """Remove item from context."""
        if item in self.items:
            self.items.remove(item)
            self.total_tokens -= int(item.token_count)
            return True
        return False
    
    def get_messages(self) -> List[LLMMessage]:
        """Convert to LLM messages, properly ordered."""
        # Sort by priority and timestamp
        sorted_items = sorted(
            self.items,
            key=lambda x: (x.priority.value, x.timestamp)
        )
        
        messages = []
        current_system = []
        current_user = []
        
        for item in sorted_items:
            if item.context_type == ContextType.SYSTEM:
                current_system.append(item.content)
            elif item.context_type == ContextType.PLAN:
                current_user.append(f"**Current Plan:**\n{item.content}")
            elif item.context_type == ContextType.KNOWLEDGE:
                current_user.append(f"**Knowledge Context:**\n{item.content}")
            elif item.context_type == ContextType.FILE_REFERENCE:
                current_user.append(f"**File Reference:**\n{item.content}")
            elif item.context_type == ContextType.ERROR:
                current_user.append(f"**Error Information:**\n{item.content}")
            elif item.context_type == ContextType.TOOL_DEFINITION:
                current_system.append(f"**Available Tools:**\n{item.content}")
            else:
                current_user.append(item.content)
        
        # Build messages
        if current_system:
            messages.append(LLMMessage(
                role="system",
                content="\n\n".join(current_system)
            ))
        
        if current_user:
            messages.append(LLMMessage(
                role="user", 
                content="\n\n".join(current_user)
            ))
        
        return messages


class ContextManager:
    """
    Manages context for LLM interactions following the 6 principles.
    
    Principles Implementation:
    1. KV-Cache Optimization: Reuse context items with consistent cache keys
    2. Tool Availability: Static tool definitions with selective masking
    3. File System as Context: Reference files instead of including full content
    4. Attention via Recitation: Periodic plan and goal injection
    5. Error Retention: Preserve all error information for learning
    6. Context Diversity: Avoid repetitive patterns in context selection
    """
    
    def __init__(
        self,
        link_engine: BidirectionalLinkEngine,
        max_context_tokens: int = 4000,
        cache_size: int = 1000
    ):
        """Initialize the context manager."""
        self.link_engine = link_engine
        self.max_context_tokens = max_context_tokens
        
        # Context storage
        self.context_cache: Dict[str, ContextItem] = {}
        self.active_context: ContextWindow = ContextWindow(max_tokens=max_context_tokens)
        
        # KV-Cache optimization
        self.cache_hit_history: deque = deque(maxlen=cache_size)
        self.content_fingerprints: Set[str] = set()
        
        # Tool availability management
        self.available_tools: Dict[str, Dict[str, Any]] = {}
        self.masked_tools: Set[str] = set()
        
        # Plan and error tracking
        self.current_plan: Optional[str] = None
        self.error_history: List[ContextItem] = []
        self.plan_injection_frequency: int = 5  # Inject plan every 5 interactions
        self.interaction_count: int = 0
        
        # Diversity tracking
        self.recent_contexts: deque = deque(maxlen=10)
        self.content_patterns: defaultdict = defaultdict(int)
        
        logger.info("ContextManager initialized with 6-principle optimization")
    
    def add_system_context(self, content: str, priority: ContextPriority = ContextPriority.CRITICAL) -> str:
        """Add system-level context (Principle 1: KV-Cache)."""
        item = ContextItem(
            content=content,
            context_type=ContextType.SYSTEM,
            priority=priority
        )
        
        # Check for cache hit
        if item.cache_key in self.context_cache:
            cached_item = self.context_cache[item.cache_key]
            cached_item.access_count += 1
            cached_item.last_access = time.time()
            self.cache_hit_history.append(item.cache_key)
            logger.debug(f"Cache hit for system context: {item.cache_key}")
            return item.cache_key
        
        # Store in cache and active context
        self.context_cache[item.cache_key] = item
        self.active_context.add_item(item)
        
        logger.debug(f"Added system context: {len(content)} chars")
        return item.cache_key
    
    def set_current_plan(self, plan: str) -> str:
        """Set the current plan (Principle 4: Attention via Recitation)."""
        self.current_plan = plan
        
        item = ContextItem(
            content=plan,
            context_type=ContextType.PLAN,
            priority=ContextPriority.HIGH
        )
        
        # Remove previous plan
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
        """Add knowledge context (Principle 3: File System as Context)."""
        # Get note analysis
        analysis = self.link_engine.analyze_note(note_id)
        if not analysis:
            logger.warning(f"Note not found for context: {note_id}")
            return ""
        
        # Use appropriate context layer
        if context_layer not in analysis.context_layers:
            context_layer = "title"  # Fallback to title
        
        content = analysis.context_layers[context_layer]
        
        # Add file reference information
        metadata = self.link_engine.note_metadata.get(note_id, {})
        file_ref = f"File: {note_id}\n"
        file_ref += f"Title: {metadata.get('title', note_id)}\n"
        file_ref += f"Links: {len(analysis.outgoing_links)} out, {len(analysis.incoming_links)} in\n"
        file_ref += f"Content: {content}"
        
        item = ContextItem(
            content=file_ref,
            context_type=ContextType.KNOWLEDGE,
            priority=priority,
            dependencies={note_id}
        )
        
        # Check diversity (Principle 6)
        if self._is_content_diverse(item):
            self.context_cache[item.cache_key] = item
            if self.active_context.add_item(item):
                logger.debug(f"Added knowledge context: {note_id} ({context_layer})")
                return item.cache_key
        else:
            logger.debug(f"Skipped non-diverse knowledge context: {note_id}")
        
        return ""
    
    def add_tool_definitions(self, tools: Dict[str, Dict[str, Any]]) -> str:
        """Add tool definitions (Principle 2: Tool Availability Management)."""
        self.available_tools.update(tools)
        
        # Filter out masked tools
        active_tools = {
            name: definition for name, definition in tools.items()
            if name not in self.masked_tools
        }
        
        if not active_tools:
            return ""
        
        # Create compact tool definitions
        tool_content = "Available tools:\n"
        for name, definition in active_tools.items():
            tool_content += f"- {name}: {definition.get('description', 'No description')}\n"
        
        item = ContextItem(
            content=tool_content,
            context_type=ContextType.TOOL_DEFINITION,
            priority=ContextPriority.MEDIUM
        )
        
        # Replace existing tool definitions
        self.active_context.items = [
            i for i in self.active_context.items 
            if i.context_type != ContextType.TOOL_DEFINITION
        ]
        
        self.context_cache[item.cache_key] = item
        self.active_context.add_item(item)
        
        logger.debug(f"Added {len(active_tools)} tool definitions")
        return item.cache_key
    
    def mask_tools(self, tool_names: List[str]):
        """Mask tools from availability (Principle 2)."""
        self.masked_tools.update(tool_names)
        logger.debug(f"Masked tools: {tool_names}")
    
    def unmask_tools(self, tool_names: List[str]):
        """Unmask tools for availability (Principle 2)."""
        self.masked_tools.difference_update(tool_names)
        logger.debug(f"Unmasked tools: {tool_names}")
    
    def add_error_context(self, error_info: str, error_type: str = "general") -> str:
        """Add error information (Principle 5: Error Information Retention)."""
        error_content = f"Error Type: {error_type}\n"
        error_content += f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        error_content += f"Details: {error_info}"
        
        item = ContextItem(
            content=error_content,
            context_type=ContextType.ERROR,
            priority=ContextPriority.CRITICAL
        )
        
        # Always preserve errors
        self.context_cache[item.cache_key] = item
        self.error_history.append(item)
        
        # Add to active context if space available
        if not self.active_context.add_item(item):
            # If no space, remove lower priority items
            self._make_space_for_critical(item)
        
        logger.warning(f"Added error context: {error_type}")
        return item.cache_key
    
    def add_file_reference(self, file_path: str, content_preview: str = "") -> str:
        """Add file reference (Principle 3: File System as Context)."""
        path_obj = Path(file_path)
        
        ref_content = f"File: {path_obj.name}\n"
        ref_content += f"Path: {file_path}\n"
        
        if content_preview:
            ref_content += f"Preview: {content_preview[:200]}..."
        else:
            # Try to get actual preview
            try:
                if path_obj.exists() and path_obj.is_file():
                    with open(path_obj, 'r', encoding='utf-8') as f:
                        preview = f.read(200)
                        ref_content += f"Preview: {preview}..."
            except Exception as e:
                ref_content += f"(Preview unavailable: {e})"
        
        item = ContextItem(
            content=ref_content,
            context_type=ContextType.FILE_REFERENCE,
            priority=ContextPriority.MEDIUM,
            dependencies={file_path}
        )
        
        self.context_cache[item.cache_key] = item
        if self.active_context.add_item(item):
            logger.debug(f"Added file reference: {file_path}")
            return item.cache_key
        
        return ""
    
    def build_context_window(self, additional_messages: List[LLMMessage] = None) -> List[LLMMessage]:
        """Build optimized context window following all 6 principles."""
        self.interaction_count += 1
        
        # Principle 4: Periodic plan injection
        if (self.interaction_count % self.plan_injection_frequency == 0 and 
            self.current_plan and 
            not any(item.context_type == ContextType.PLAN for item in self.active_context.items)):
            self.set_current_plan(self.current_plan)
        
        # Get base messages from context window
        messages = self.active_context.get_messages()
        
        # Add additional messages
        if additional_messages:
            messages.extend(additional_messages)
        
        # Update diversity tracking
        self._update_diversity_tracking(messages)
        
        # Log context statistics
        self._log_context_stats()
        
        return messages
    
    def optimize_context(self):
        """Optimize context following all principles."""
        logger.debug("Starting context optimization")
        
        # Principle 1: KV-Cache optimization - prioritize frequently accessed items
        for item in self.active_context.items:
            if item.cache_key in self.cache_hit_history:
                item.priority = ContextPriority.HIGH
        
        # Remove stale or low-priority items if over budget
        if self.active_context.total_tokens > self.max_context_tokens * 0.9:
            self._trim_context()
        
        # Principle 6: Ensure diversity
        self._ensure_diversity()
        
        logger.debug("Context optimization completed")
    
    def get_related_knowledge(self, query: str, max_items: int = 3) -> List[str]:
        """Get related knowledge using bidirectional links."""
        # Simple keyword matching for now
        # In a full implementation, this would use semantic search
        related_notes = []
        
        query_lower = query.lower()
        for note_id, metadata in self.link_engine.note_metadata.items():
            title = metadata.get('title', '').lower()
            content = self.link_engine.note_content.get(note_id, '').lower()
            
            if query_lower in title or query_lower in content:
                related_notes.append(note_id)
                
                if len(related_notes) >= max_items:
                    break
        
        # Add knowledge context for related notes
        context_keys = []
        for note_id in related_notes:
            key = self.add_knowledge_context(note_id, context_layer="summary")
            if key:
                context_keys.append(key)
        
        return context_keys
    
    def _is_content_diverse(self, item: ContextItem) -> bool:
        """Check if content adds diversity (Principle 6)."""
        # Generate content fingerprint
        fingerprint = hashlib.md5(item.content.encode()).hexdigest()
        
        if fingerprint in self.content_fingerprints:
            return False
        
        # Check for similar patterns
        words = set(item.content.lower().split())
        for recent_context in self.recent_contexts:
            recent_words = set(recent_context.lower().split())
            overlap = len(words & recent_words) / len(words | recent_words)
            
            if overlap > 0.7:  # 70% similarity threshold
                return False
        
        self.content_fingerprints.add(fingerprint)
        return True
    
    def _make_space_for_critical(self, critical_item: ContextItem):
        """Make space for critical items by removing low priority ones."""
        # Remove lowest priority items until we have space
        sorted_items = sorted(
            self.active_context.items,
            key=lambda x: (x.priority.value, -x.access_count),
            reverse=True
        )
        
        for item in sorted_items:
            if item.priority.value > ContextPriority.HIGH.value:
                if self.active_context.remove_item(item):
                    if self.active_context.total_tokens + critical_item.token_count <= self.max_context_tokens:
                        self.active_context.add_item(critical_item)
                        break
    
    def _trim_context(self):
        """Trim context to fit within budget."""
        # Sort by priority and access frequency
        sorted_items = sorted(
            self.active_context.items,
            key=lambda x: (x.priority.value, -x.access_count, -x.last_access)
        )
        
        # Keep high priority items, remove others if needed
        new_items = []
        total_tokens = 0
        
        for item in sorted_items:
            if total_tokens + item.token_count <= self.max_context_tokens:
                new_items.append(item)
                total_tokens += int(item.token_count)
            elif item.priority.value <= ContextPriority.HIGH.value:
                # Always keep high priority items
                new_items.append(item)
                total_tokens += int(item.token_count)
        
        self.active_context.items = new_items
        self.active_context.total_tokens = total_tokens
        
        logger.debug(f"Trimmed context to {len(new_items)} items, {total_tokens} tokens")
    
    def _ensure_diversity(self):
        """Ensure context diversity (Principle 6)."""
        # Remove duplicate or very similar items
        unique_items = []
        seen_fingerprints = set()
        
        for item in self.active_context.items:
            fingerprint = hashlib.md5(item.content.encode()).hexdigest()
            
            if fingerprint not in seen_fingerprints:
                unique_items.append(item)
                seen_fingerprints.add(fingerprint)
        
        if len(unique_items) < len(self.active_context.items):
            self.active_context.items = unique_items
            self.active_context.total_tokens = sum(int(item.token_count) for item in unique_items)
            logger.debug(f"Removed {len(self.active_context.items) - len(unique_items)} duplicate items")
    
    def _update_diversity_tracking(self, messages: List[LLMMessage]):
        """Update diversity tracking with current messages."""
        content = " ".join(msg.content for msg in messages)
        self.recent_contexts.append(content)
        
        # Update pattern frequency
        words = content.lower().split()
        for word in words:
            self.content_patterns[word] += 1
    
    def _log_context_stats(self):
        """Log context statistics for monitoring."""
        stats = {
            "total_items": len(self.active_context.items),
            "total_tokens": self.active_context.total_tokens,
            "cache_hits": len(self.cache_hit_history),
            "error_count": len(self.error_history),
            "available_tools": len(self.available_tools) - len(self.masked_tools),
            "masked_tools": len(self.masked_tools)
        }
        
        logger.debug(f"Context stats: {stats}")
    
    def clear_context(self):
        """Clear all context (useful for testing)."""
        self.active_context = ContextWindow(max_tokens=self.max_context_tokens)
        self.context_cache.clear()
        self.content_fingerprints.clear()
        self.recent_contexts.clear()
        self.content_patterns.clear()
        logger.info("Context cleared")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context state."""
        type_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        
        for item in self.active_context.items:
            type_counts[item.context_type.value] += 1
            priority_counts[item.priority.value] += 1
        
        return {
            "total_items": len(self.active_context.items),
            "total_tokens": self.active_context.total_tokens,
            "token_utilization": self.active_context.total_tokens / self.max_context_tokens,
            "types": dict(type_counts),
            "priorities": dict(priority_counts),
            "cache_hit_rate": len(self.cache_hit_history) / max(1, self.interaction_count),
            "current_plan": bool(self.current_plan),
            "error_count": len(self.error_history),
            "diversity_score": len(self.content_fingerprints) / max(1, len(self.recent_contexts))
        }