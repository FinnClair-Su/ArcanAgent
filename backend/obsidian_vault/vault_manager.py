"""
Vault Manager - Core Obsidian-style Knowledge Base Manager
Manages markdown files, bidirectional links, and knowledge graph
"""

import os
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
import hashlib

from .markdown_parser import MarkdownParser
from .bidirectional_links import BidirectionalLinks
from .link_graph import LinkGraph
from .fsrs_scheduler import FSRSScheduler


logger = logging.getLogger(__name__)


class VaultManager:
    """Obsidian-style vault manager for markdown knowledge base"""
    
    def __init__(self, vault_path: str = "data/vault"):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.parser = MarkdownParser()
        self.links = BidirectionalLinks()
        self.graph = LinkGraph()
        self.fsrs = FSRSScheduler()
        
        # In-memory indexes
        self.note_index: Dict[str, Dict[str, Any]] = {}
        self.title_index: Dict[str, str] = {}  # title -> file_id
        self.tag_index: Dict[str, Set[str]] = {}  # tag -> set(file_ids)
        
        # Initialize vault
        self._initialize_vault()
    
    async def _initialize_vault(self):
        """Initialize vault and build indexes"""
        logger.info(f"Initializing vault at {self.vault_path}")
        
        # Create default directories
        self._create_default_structure()
        
        # Build indexes from existing files
        await self._rebuild_indexes()
        
        logger.info("Vault initialized successfully")
    
    def _create_default_structure(self):
        """Create default vault directory structure"""
        directories = [
            "concepts",      # Core concepts and knowledge
            "conversations", # Daily conversation logs
            "topics",        # Topic-based organization
            "reviews",       # FSRS review materials
            "templates",     # Note templates
            "assets"         # Images and attachments
        ]
        
        for directory in directories:
            (self.vault_path / directory).mkdir(exist_ok=True)
    
    async def _rebuild_indexes(self):
        """Rebuild all indexes from existing markdown files"""
        logger.info("Rebuilding vault indexes...")
        
        # Clear existing indexes
        self.note_index.clear()
        self.title_index.clear()
        self.tag_index.clear()
        
        # Scan all markdown files
        for md_file in self.vault_path.rglob("*.md"):
            if md_file.is_file():
                await self._index_file(md_file)
        
        # Build link graph
        await self.graph.build_graph(self.note_index)
        
        logger.info(f"Indexed {len(self.note_index)} notes")
    
    async def _index_file(self, file_path: Path):
        """Index a single markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse markdown
            parsed = await self.parser.parse_markdown(content)
            
            # Generate file ID
            file_id = self._generate_file_id(file_path)
            
            # Update indexes
            self.note_index[file_id] = {
                "path": str(file_path),
                "title": parsed["frontmatter"].get("title", file_path.stem),
                "content": parsed["content"],
                "frontmatter": parsed["frontmatter"],
                "links": parsed["links"],
                "updated": datetime.fromisoformat(
                    parsed["frontmatter"].get("updated", datetime.now().isoformat())
                )
            }
            
            # Title index
            title = parsed["frontmatter"].get("title", file_path.stem)
            self.title_index[title.lower()] = file_id
            
            # Tag index
            tags = parsed["frontmatter"].get("tags", [])
            for tag in tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = set()
                self.tag_index[tag].add(file_id)
            
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}")
    
    def _generate_file_id(self, file_path: Path) -> str:
        """Generate unique file ID based on path"""
        relative_path = file_path.relative_to(self.vault_path)
        return hashlib.md5(str(relative_path).encode()).hexdigest()[:8]
    
    async def create_note(
        self, 
        title: str, 
        content: str = "", 
        directory: str = "concepts",
        tags: List[str] = None,
        links: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a new markdown note"""
        
        # Sanitize title for filename
        filename = self._sanitize_filename(title) + ".md"
        file_path = self.vault_path / directory / filename
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate file ID
        file_id = self._generate_file_id(file_path)
        
        # Prepare frontmatter
        frontmatter = {
            "id": file_id,
            "title": title,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "tags": tags or [],
            "links": {
                "outgoing": len(links) if links else 0,
                "incoming": 0,
                "density": 0.0
            }
        }
        
        # Add custom metadata
        if metadata:
            frontmatter.update(metadata)
        
        # Add FSRS data if not present
        if "fsrs" not in frontmatter:
            frontmatter["fsrs"] = await self.fsrs.initialize_note_fsrs()
        
        # Build full content with frontmatter
        full_content = self._build_markdown_content(frontmatter, content)
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        # Update indexes
        await self._index_file(file_path)
        
        # Update bidirectional links
        if links:
            await self.links.add_links(file_id, links)
        
        # Update link graph
        await self.graph.add_note(file_id, self.note_index[file_id])
        
        logger.info(f"Created note: {title} (ID: {file_id})")
        return file_id
    
    async def update_note(
        self, 
        file_id: str, 
        content: str = None,
        title: str = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Update an existing note"""
        
        if file_id not in self.note_index:
            logger.warning(f"Note not found: {file_id}")
            return False
        
        note = self.note_index[file_id]
        file_path = Path(note["path"])
        
        # Read current content
        with open(file_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        parsed = await self.parser.parse_markdown(current_content)
        frontmatter = parsed["frontmatter"]
        
        # Update frontmatter
        frontmatter["updated"] = datetime.now().isoformat()
        
        if title:
            frontmatter["title"] = title
        if tags is not None:
            frontmatter["tags"] = tags
        if metadata:
            frontmatter.update(metadata)
        
        # Use new content or keep existing
        note_content = content if content is not None else parsed["content"]
        
        # Build updated markdown
        full_content = self._build_markdown_content(frontmatter, note_content)
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        # Re-index file
        await self._index_file(file_path)
        
        # Update link graph
        await self.graph.update_note(file_id, self.note_index[file_id])
        
        logger.info(f"Updated note: {file_id}")
        return True
    
    async def get_note(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get note by ID or title"""
        
        # Try by ID first
        if identifier in self.note_index:
            return self.note_index[identifier]
        
        # Try by title
        file_id = self.title_index.get(identifier.lower())
        if file_id:
            return self.note_index.get(file_id)
        
        return None
    
    async def search_notes(
        self,
        query: str = None,
        tags: List[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search notes by query and/or tags"""
        
        results = []
        
        for file_id, note in self.note_index.items():
            match_score = 0
            
            # Text search
            if query:
                query_lower = query.lower()
                if query_lower in note["title"].lower():
                    match_score += 2
                if query_lower in note["content"].lower():
                    match_score += 1
            
            # Tag filtering
            if tags:
                note_tags = set(note["frontmatter"].get("tags", []))
                tag_matches = len(set(tags) & note_tags)
                if tag_matches > 0:
                    match_score += tag_matches
                elif tags:  # Required tags not found
                    continue
            
            if match_score > 0 or (not query and not tags):
                results.append({
                    "note": note,
                    "score": match_score,
                    "file_id": file_id
                })
        
        # Sort by score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    async def delete_note(self, file_id: str) -> bool:
        """Delete a note and update all references"""
        
        if file_id not in self.note_index:
            return False
        
        note = self.note_index[file_id]
        file_path = Path(note["path"])
        
        # Remove bidirectional links
        await self.links.remove_note_links(file_id)
        
        # Remove from graph
        await self.graph.remove_note(file_id)
        
        # Delete file
        if file_path.exists():
            file_path.unlink()
        
        # Remove from indexes
        title = note["title"].lower()
        if title in self.title_index:
            del self.title_index[title]
        
        for tag in note["frontmatter"].get("tags", []):
            if tag in self.tag_index:
                self.tag_index[tag].discard(file_id)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
        
        del self.note_index[file_id]
        
        logger.info(f"Deleted note: {file_id}")
        return True
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title for use as filename"""
        import re
        # Remove invalid characters and limit length
        sanitized = re.sub(r'[<>:"/\\|?*]', '', title)
        sanitized = sanitized.strip().replace(' ', '_')
        return sanitized[:50]  # Limit length
    
    def _build_markdown_content(self, frontmatter: Dict[str, Any], content: str) -> str:
        """Build complete markdown content with frontmatter"""
        
        yaml_content = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
        
        return f\"\"\"---\n{yaml_content}---\n\n{content}\"\"\"\n    \n    async def get_vault_statistics(self) -> Dict[str, Any]:\n        \"\"\"Get vault statistics\"\"\"\n        \n        total_notes = len(self.note_index)\n        total_links = await self.graph.get_total_links()\n        \n        # Calculate tag distribution\n        tag_distribution = {tag: len(file_ids) for tag, file_ids in self.tag_index.items()}\n        \n        # Get directory distribution\n        directory_distribution = {}\n        for note in self.note_index.values():\n            path = Path(note[\"path\"])\n            directory = path.parent.name\n            directory_distribution[directory] = directory_distribution.get(directory, 0) + 1\n        \n        return {\n            \"total_notes\": total_notes,\n            \"total_links\": total_links,\n            \"total_tags\": len(self.tag_index),\n            \"tag_distribution\": tag_distribution,\n            \"directory_distribution\": directory_distribution,\n            \"vault_path\": str(self.vault_path)\n        }"