"""
The Empress - Markdown Knowledge Vault Manager Agent
MCP Capabilities: manage_markdown_vault, create_bidirectional_links, update_user_knowledge
Responsibility: All Obsidian-style markdown knowledge vault management and maintenance
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.agents.base_agent import BaseAgent
from backend.mcp import MCPCapability, MCPCapabilityType
from backend.obsidian_vault import VaultManager, BidirectionalLinks, LinkGraph, ContextBuilder
from backend.database.repositories.knowledge_repo import KnowledgeRepository


logger = logging.getLogger(__name__)


class TheEmpress(BaseAgent):
    """The Empress - Markdown Knowledge Vault Manager"""
    
    def __init__(self):
        super().__init__(
            agent_id="the_empress",
            name="The Empress",
            description="Markdown knowledge vault manager specializing in bidirectional links and concept relationships"
        )
        self.vault_manager = VaultManager()
        self.bidirectional_links = BidirectionalLinks()
        self.link_graph = LinkGraph()
        self.context_builder = ContextBuilder(self.vault_manager, self.link_graph, None)
        self.knowledge_repo = KnowledgeRepository()
        
    async def _initialize(self):
        """Initialize The Empress agent"""
        await self.vault_manager._initialize_vault()
        await self.knowledge_repo.initialize()
        logger.info("The Empress markdown vault systems initialized")
    
    async def _shutdown(self):
        """Shutdown The Empress agent"""
        await self.knowledge_repo.shutdown()
        logger.info("The Empress markdown vault systems shut down")
    
    async def _register_capabilities(self):
        """Register markdown vault management capabilities"""
        self.capabilities = [
            MCPCapability(
                name="markdown_vault_management",
                capability_type=MCPCapabilityType.KNOWLEDGE,
                description="Comprehensive markdown knowledge vault management with bidirectional links",
                methods={
                    "manage_markdown_vault": {
                        "description": "Manage and maintain markdown knowledge vault",
                        "parameters": {
                            "operation": "string",
                            "data": "object"
                        }
                    },
                    "create_bidirectional_links": {
                        "description": "Create and maintain [[bidirectional links]] between notes",
                        "parameters": {
                            "source_note": "string",
                            "target_notes": "array",
                            "link_type": "string"
                        }
                    },
                    "update_note_content": {
                        "description": "Create or update markdown note content",
                        "parameters": {
                            "note_id": "string",
                            "title": "string", 
                            "content": "string",
                            "tags": "array",
                            "metadata": "object"
                        }
                    },
                    "analyze_link_density": {
                        "description": "Analyze link density to determine content granularity",
                        "parameters": {
                            "note_id": "string"
                        }
                    },
                    "search_vault": {
                        "description": "Search markdown vault with bidirectional link traversal",
                        "parameters": {
                            "query": "string",
                            "search_type": "string",
                            "limit": "number"
                        }
                    },
                    "build_context_graph": {
                        "description": "Build context graph for LLM queries using shortest paths",
                        "parameters": {
                            "query": "string",
                            "user_knowledge": "array",
                            "max_context_size": "number"
                        }
                    }
                },
                agent_id=self.agent_id,
                version="2.0.0"
            )
        ]
    
    async def manage_markdown_vault(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Manage markdown vault operations"""
        operation = payload.get("operation")
        data = payload.get("data", {})
        
        logger.info(f"Managing markdown vault: {operation}")
        
        result = None
        if operation == "create_note":
            result = await self.vault_manager.create_note(
                title=data.get("title"),
                content=data.get("content", ""),
                directory=data.get("directory", "concepts"),
                tags=data.get("tags", []),
                metadata=data.get("metadata", {})
            )
        elif operation == "update_note":
            result = await self.vault_manager.update_note(
                file_id=data.get("note_id"),
                content=data.get("content"),
                title=data.get("title"),
                tags=data.get("tags"),
                metadata=data.get("metadata")
            )
        elif operation == "delete_note":
            result = await self.vault_manager.delete_note(data.get("note_id"))
        elif operation == "get_statistics":
            result = await self.vault_manager.get_vault_statistics()
        
        return {"operation": operation, "result": result}
    
    async def create_bidirectional_links(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create bidirectional links between notes"""
        source_note = payload.get("source_note")
        target_notes = payload.get("target_notes", [])
        link_type = payload.get("link_type", "relates_to")
        
        logger.info(f"Creating bidirectional links from {source_note} to {target_notes}")
        
        # Update the source note's content to include links
        source_note_data = await self.vault_manager.get_note(source_note)
        if not source_note_data:
            return {"error": "Source note not found"}
        
        # Add links to content
        updated_content = source_note_data["content"]
        for target in target_notes:
            target_note_data = await self.vault_manager.get_note(target)
            if target_note_data:
                target_title = target_note_data["title"]
                if f"[[{target_title}]]" not in updated_content:
                    updated_content += f"\n\n关联概念: [[{target_title}]]"
        
        # Update source note
        await self.vault_manager.update_note(
            file_id=source_note,
            content=updated_content
        )
        
        # Update bidirectional links
        await self.bidirectional_links.add_links(source_note, target_notes)
        
        return {
            "source_note": source_note,
            "target_notes": target_notes,
            "links_created": len(target_notes),
            "link_type": link_type
        }
    
    async def update_note_content(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update note content"""
        note_id = payload.get("note_id")
        title = payload.get("title")
        content = payload.get("content", "")
        tags = payload.get("tags", [])
        metadata = payload.get("metadata", {})
        
        logger.info(f"Updating note content: {title}")
        
        if note_id:
            # Update existing note
            success = await self.vault_manager.update_note(
                file_id=note_id,
                content=content,
                title=title,
                tags=tags,
                metadata=metadata
            )
            result = {"note_id": note_id, "updated": success}
        else:
            # Create new note
            new_note_id = await self.vault_manager.create_note(
                title=title,
                content=content,
                tags=tags,
                metadata=metadata
            )
            result = {"note_id": new_note_id, "created": True}
        
        return result
    
    async def analyze_link_density(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze link density to determine content granularity"""
        note_id = payload.get("note_id")
        
        if not note_id:
            return {"error": "Note ID required"}
        
        logger.info(f"Analyzing link density for note: {note_id}")
        
        # Get outgoing and incoming links
        outgoing_links = self.bidirectional_links.get_outgoing_links(note_id)
        incoming_links = self.bidirectional_links.get_incoming_links(note_id)
        
        # Calculate density metrics
        outgoing_count = len(outgoing_links)
        incoming_count = len(incoming_links)
        total_links = outgoing_count + incoming_count
        
        # Determine granularity based on link density
        if total_links > 10:
            granularity = "high"  # Needs to be split into smaller notes
            recommendation = "Consider splitting this note into more focused sub-topics"
        elif total_links > 5:
            granularity = "medium"  # Good level of detail
            recommendation = "Good level of detail and connections"
        else:
            granularity = "low"  # Could be expanded
            recommendation = "Consider adding more connections or detail"
        
        # Calculate importance score
        importance_score = min((incoming_count * 0.7 + outgoing_count * 0.3) / 10, 1.0)
        
        return {
            "note_id": note_id,
            "outgoing_links": outgoing_count,
            "incoming_links": incoming_count,
            "total_links": total_links,
            "link_density": self.bidirectional_links.get_link_density(note_id),
            "granularity": granularity,
            "importance_score": importance_score,
            "recommendation": recommendation
        }
    
    async def search_vault(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Search markdown vault with bidirectional link traversal"""
        query = payload.get("query")
        search_type = payload.get("search_type", "comprehensive")
        limit = payload.get("limit", 10)
        
        logger.info(f"Searching vault: {query}")
        
        # Perform search
        results = await self.vault_manager.search_notes(
            query=query,
            limit=limit
        )
        
        # Enhance results with link information
        enhanced_results = []
        for result in results:
            note_id = result["file_id"]
            note_data = result["note"]
            
            # Get link information
            outgoing = len(self.bidirectional_links.get_outgoing_links(note_id))
            incoming = len(self.bidirectional_links.get_incoming_links(note_id))
            
            enhanced_results.append({
                "note_id": note_id,
                "title": note_data["title"],
                "content_preview": note_data["content"][:200] + "..." if len(note_data["content"]) > 200 else note_data["content"],
                "relevance_score": result["score"],
                "outgoing_links": outgoing,
                "incoming_links": incoming,
                "tags": note_data["frontmatter"].get("tags", [])
            })
        
        return {
            "query": query,
            "results": enhanced_results,
            "total_found": len(enhanced_results),
            "search_type": search_type
        }
    
    async def build_context_graph(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Build context graph for LLM queries using shortest paths"""
        query = payload.get("query")
        user_knowledge = payload.get("user_knowledge", [])
        max_context_size = payload.get("max_context_size", 15)
        
        logger.info(f"Building context graph for query: {query}")
        
        # Use context builder to create optimized context
        context_result = await self.context_builder.build_comprehensive_context(
            query=query,
            user_knowledge=user_knowledge
        )
        
        # Limit context size if requested
        if max_context_size and len(context_result["context_notes"]) > max_context_size:
            context_result["context_notes"] = context_result["context_notes"][:max_context_size]
            context_result["total_notes"] = len(context_result["context_notes"])
        
        return context_result"