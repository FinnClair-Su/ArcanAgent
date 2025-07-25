"""
Note Manager

Manages markdown notes in the knowledge base with full Obsidian compatibility.
Works closely with the BidirectionalLinkEngine to maintain link integrity.
"""

import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import frontmatter
import logging
from dataclasses import dataclass

from backend.core.bidirectional_links import BidirectionalLinkEngine

logger = logging.getLogger("ArcanAgent.NoteManager")


@dataclass
class NoteInfo:
    """Information about a note."""
    id: str
    title: str
    file_path: Path
    metadata: Dict[str, Any]
    created: datetime.datetime
    modified: datetime.datetime
    tags: List[str]
    complexity: Optional[int] = None
    mastery_level: Optional[int] = None


class NoteManager:
    """
    Manages the knowledge base notes with full Obsidian compatibility.
    
    Responsibilities:
    - CRUD operations on markdown notes
    - Metadata management (frontmatter)
    - File system organization
    - Integration with BidirectionalLinkEngine
    - Automatic link updates when notes are renamed/moved
    """
    
    def __init__(self, knowledge_base_path: str, link_engine: BidirectionalLinkEngine):
        """Initialize the note manager."""
        self.knowledge_base_path = Path(knowledge_base_path)
        self.notes_path = self.knowledge_base_path / "notes"
        self.link_engine = link_engine
        
        # Ensure notes directory exists
        self.notes_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized NoteManager with path: {self.notes_path}")
    
    def create_note(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        complexity: Optional[int] = None,
        subdirectory: Optional[str] = None
    ) -> str:
        """
        Create a new note in the knowledge base.
        
        Args:
            title: Note title
            content: Note content (markdown)
            tags: Optional list of tags
            complexity: Optional complexity level (1-10)
            subdirectory: Optional subdirectory within notes/
            
        Returns:
            Note ID (relative path without .md extension)
        """
        # Generate filename from title
        filename = self._title_to_filename(title)
        
        # Determine file path
        if subdirectory:
            target_dir = self.notes_path / subdirectory
            target_dir.mkdir(parents=True, exist_ok=True)
            file_path = target_dir / f"{filename}.md"
            note_id = f"{subdirectory}/{filename}"
        else:
            file_path = self.notes_path / f"{filename}.md"
            note_id = filename
        
        # Check if note already exists
        if file_path.exists():
            counter = 1
            while True:
                if subdirectory:
                    new_filename = f"{filename}_{counter}"
                    file_path = self.notes_path / subdirectory / f"{new_filename}.md"
                    note_id = f"{subdirectory}/{new_filename}"
                else:
                    new_filename = f"{filename}_{counter}"
                    file_path = self.notes_path / f"{new_filename}.md"
                    note_id = new_filename
                
                if not file_path.exists():
                    break
                counter += 1
        
        # Create note with frontmatter
        now = datetime.datetime.now().isoformat()
        metadata = {
            'title': title,
            'created': now,
            'modified': now,
            'tags': tags or [],
        }
        
        if complexity is not None:
            metadata['complexity'] = complexity
        
        # Create the note
        post = frontmatter.Post(content, **metadata)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        logger.info(f"Created note: {note_id}")
        
        # Refresh the link engine to include the new note
        self.link_engine.refresh_knowledge_base()
        
        return note_id
    
    def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a note by ID.
        
        Args:
            note_id: Note identifier
            
        Returns:
            Dict containing note data or None if not found
        """
        file_path = self.notes_path / f"{note_id}.md"
        
        if not file_path.exists():
            logger.warning(f"Note not found: {note_id}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Get link analysis
            link_analysis = self.link_engine.analyze_note(note_id)
            
            return {
                'id': note_id,
                'metadata': dict(post.metadata),
                'content': post.content,
                'file_path': str(file_path),
                'outgoing_links': list(link_analysis.outgoing_links) if link_analysis else [],
                'incoming_links': list(link_analysis.incoming_links) if link_analysis else []
            }
            
        except Exception as e:
            logger.error(f"Error reading note {note_id}: {e}")
            return None
    
    def update_note(
        self,
        note_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        complexity: Optional[int] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing note.
        
        Args:
            note_id: Note identifier
            title: New title (optional)
            content: New content (optional)
            tags: New tags (optional)
            complexity: New complexity level (optional)
            additional_metadata: Additional metadata to update
            
        Returns:
            True if successful, False otherwise
        """
        file_path = self.notes_path / f"{note_id}.md"
        
        if not file_path.exists():
            logger.warning(f"Note not found for update: {note_id}")
            return False
        
        try:
            # Read existing note
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Update metadata
            if title is not None:
                post.metadata['title'] = title
            if tags is not None:
                post.metadata['tags'] = tags
            if complexity is not None:
                post.metadata['complexity'] = complexity
            if additional_metadata:
                post.metadata.update(additional_metadata)
            
            # Always update modified timestamp
            post.metadata['modified'] = datetime.datetime.now().isoformat()
            
            # Update content if provided
            if content is not None:
                post.content = content
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter.dumps(post))
            
            logger.info(f"Updated note: {note_id}")
            
            # Refresh link engine if content was changed (links might have changed)
            if content is not None:
                self.link_engine.refresh_knowledge_base()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating note {note_id}: {e}")
            return False
    
    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note from the knowledge base.
        
        Args:
            note_id: Note identifier
            
        Returns:
            True if successful, False otherwise
        """
        file_path = self.notes_path / f"{note_id}.md"
        
        if not file_path.exists():
            logger.warning(f"Note not found for deletion: {note_id}")
            return False
        
        try:
            # Get incoming links before deletion to warn about broken links
            link_analysis = self.link_engine.analyze_note(note_id)
            if link_analysis and link_analysis.incoming_links:
                logger.warning(f"Deleting note {note_id} will break links from: {link_analysis.incoming_links}")
            
            # Delete the file
            file_path.unlink()
            
            logger.info(f"Deleted note: {note_id}")
            
            # Refresh link engine to remove from index
            self.link_engine.refresh_knowledge_base()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting note {note_id}: {e}")
            return False
    
    def list_notes(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        tags_filter: Optional[List[str]] = None,
        search_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List notes with optional filtering and pagination.
        
        Args:
            limit: Maximum number of notes to return
            offset: Number of notes to skip
            tags_filter: Filter by tags (AND logic)
            search_query: Search in title and content
            
        Returns:
            Dict containing notes list and pagination info
        """
        all_notes = []
        
        # Walk through all markdown files
        for file_path in self.notes_path.rglob("*.md"):
            try:
                note_id = str(file_path.relative_to(self.notes_path)).replace('.md', '')
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                metadata = dict(post.metadata)
                content = post.content
                
                # Apply filters
                if tags_filter:
                    note_tags = metadata.get('tags', [])
                    if not all(tag in note_tags for tag in tags_filter):
                        continue
                
                if search_query:
                    title = metadata.get('title', '')
                    if search_query.lower() not in title.lower() and search_query.lower() not in content.lower():
                        continue
                
                # Get link analysis
                link_analysis = self.link_engine.analyze_note(note_id)
                
                note_info = {
                    'id': note_id,
                    'title': metadata.get('title', note_id),
                    'tags': metadata.get('tags', []),
                    'created': metadata.get('created'),
                    'modified': metadata.get('modified'),
                    'complexity': metadata.get('complexity'),
                    'mastery_level': metadata.get('mastery_level'),
                    'summary': metadata.get('summary'),
                    'link_count': len(link_analysis.outgoing_links) + len(link_analysis.incoming_links) if link_analysis else 0,
                    'link_density': round(link_analysis.link_density, 3) if link_analysis else 0.0
                }
                
                all_notes.append(note_info)
                
            except Exception as e:
                logger.error(f"Error processing note {file_path}: {e}")
                continue
        
        # Sort by modified date (newest first)
        all_notes.sort(key=lambda x: x.get('modified', ''), reverse=True)
        
        # Apply pagination
        total = len(all_notes)
        start_idx = offset
        end_idx = start_idx + limit if limit else len(all_notes)
        
        paginated_notes = all_notes[start_idx:end_idx]
        
        return {
            'notes': paginated_notes,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': end_idx < total
        }
    
    def search_notes(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search notes by content and metadata.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of matching notes with relevance scores
        """
        results = []
        query_lower = query.lower()
        
        for file_path in self.notes_path.rglob("*.md"):
            try:
                note_id = str(file_path.relative_to(self.notes_path)).replace('.md', '')
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                
                metadata = dict(post.metadata)
                content = post.content
                title = metadata.get('title', note_id)
                
                # Calculate relevance score
                score = 0.0
                
                # Title match (highest weight)
                if query_lower in title.lower():
                    score += 10.0
                
                # Content match
                content_matches = content.lower().count(query_lower)
                score += content_matches * 1.0
                
                # Tag match
                tags = metadata.get('tags', [])
                for tag in tags:
                    if query_lower in tag.lower():
                        score += 5.0
                
                if score > 0:
                    results.append({
                        'id': note_id,
                        'title': title,
                        'score': score,
                        'metadata': metadata,
                        'snippet': self._generate_snippet(content, query, max_length=200)
                    })
                    
            except Exception as e:
                logger.error(f"Error searching note {file_path}: {e}")
                continue
        
        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:max_results]
    
    def _title_to_filename(self, title: str) -> str:
        """Convert a title to a safe filename."""
        # Replace spaces with underscores and remove special characters
        filename = title.replace(' ', '_')
        filename = ''.join(c for c in filename if c.isalnum() or c in '_-')
        return filename.lower()
    
    def _generate_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Generate a snippet around the query match."""
        query_lower = query.lower()
        content_lower = content.lower()
        
        match_idx = content_lower.find(query_lower)
        if match_idx == -1:
            # No match found, return beginning of content
            return content[:max_length] + "..." if len(content) > max_length else content
        
        # Find a good snippet around the match
        start_idx = max(0, match_idx - max_length // 2)
        end_idx = min(len(content), start_idx + max_length)
        
        snippet = content[start_idx:end_idx]
        
        # Add ellipses if we're not at the beginning/end
        if start_idx > 0:
            snippet = "..." + snippet
        if end_idx < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def get_orphaned_notes(self) -> List[str]:
        """Get notes that have no incoming or outgoing links."""
        orphaned = []
        
        for note_id in self.link_engine.note_metadata.keys():
            analysis = self.link_engine.analyze_note(note_id)
            if analysis and not analysis.outgoing_links and not analysis.incoming_links:
                orphaned.append(note_id)
        
        return orphaned
    
    def get_most_connected_notes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most connected notes in the knowledge base."""
        note_connections = []
        
        for note_id in self.link_engine.note_metadata.keys():
            analysis = self.link_engine.analyze_note(note_id)
            if analysis:
                total_connections = len(analysis.outgoing_links) + len(analysis.incoming_links)
                note_connections.append({
                    'id': note_id,
                    'title': self.link_engine.note_metadata[note_id].get('title', note_id),
                    'total_connections': total_connections,
                    'outgoing_links': len(analysis.outgoing_links),
                    'incoming_links': len(analysis.incoming_links),
                    'link_density': analysis.link_density
                })
        
        # Sort by total connections
        note_connections.sort(key=lambda x: x['total_connections'], reverse=True)
        
        return note_connections[:limit]