"""
Notes Management API Routes

Provides endpoints for managing markdown notes in the knowledge base.
Maintains full Obsidian compatibility while providing programmatic access.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from backend.core import BidirectionalLinkEngine
from backend.knowledge import NoteManager

router = APIRouter()
logger = logging.getLogger("ArcanAgent.API.Notes")


# Dependency injection - these will be properly initialized in main_server.py
_link_engine: Optional[BidirectionalLinkEngine] = None
_note_manager: Optional[NoteManager] = None


def get_link_engine() -> BidirectionalLinkEngine:
    """Get the bidirectional link engine instance."""
    if _link_engine is None:
        raise HTTPException(status_code=500, detail="Link engine not initialized")
    return _link_engine


def get_note_manager() -> NoteManager:
    """Get the note manager instance.""" 
    if _note_manager is None:
        raise HTTPException(status_code=500, detail="Note manager not initialized")
    return _note_manager


def initialize_services(link_engine: BidirectionalLinkEngine, note_manager: NoteManager):
    """Initialize the service dependencies."""
    global _link_engine, _note_manager
    _link_engine = link_engine
    _note_manager = note_manager


# Request/Response Models
class NoteMetadata(BaseModel):
    """Note metadata model."""
    title: str
    tags: List[str] = []
    created: str
    modified: str
    complexity: Optional[int] = None
    mastery_level: Optional[int] = None
    summary: Optional[str] = None


class Note(BaseModel):
    """Complete note model."""
    id: str
    metadata: NoteMetadata
    content: str
    outgoing_links: List[str] = []
    incoming_links: List[str] = []


class CreateNoteRequest(BaseModel):
    """Request model for creating a new note."""
    title: str
    content: str
    tags: List[str] = []
    complexity: Optional[int] = None


class UpdateNoteRequest(BaseModel):
    """Request model for updating an existing note."""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    complexity: Optional[int] = None


@router.get("/")
async def list_notes(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by"),
    search: Optional[str] = Query(None, description="Search query for note content"),
    note_manager: NoteManager = Depends(get_note_manager)
) -> Dict[str, Any]:
    """
    List notes in the knowledge base with optional filtering.
    
    Args:
        limit: Maximum number of notes to return
        offset: Number of notes to skip  
        tags: Comma-separated tags to filter by
        search: Search query for note content
        
    Returns:
        Dict containing notes list and pagination info
    """
    logger.info(f"Listing notes: limit={limit}, offset={offset}, tags={tags}, search={search}")
    
    try:
        # Parse tags filter
        tags_filter = None
        if tags:
            tags_filter = [tag.strip() for tag in tags.split(",")]
        
        # Get notes using NoteManager
        result = note_manager.list_notes(
            limit=limit,
            offset=offset,
            tags_filter=tags_filter,
            search_query=search
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing notes: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing notes: {str(e)}")


@router.get("/{note_id}")
async def get_note(
    note_id: str,
    note_manager: NoteManager = Depends(get_note_manager)
) -> Note:
    """
    Get a specific note by ID.
    
    Args:
        note_id: The unique identifier for the note
        
    Returns:
        Complete note data including content and links
    """
    logger.info(f"Getting note: {note_id}")
    
    try:
        note_data = note_manager.get_note(note_id)
        
        if not note_data:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Convert to response model
        return Note(
            id=note_data['id'],
            metadata=NoteMetadata(**note_data['metadata']),
            content=note_data['content'],
            outgoing_links=note_data['outgoing_links'],
            incoming_links=note_data['incoming_links']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting note {note_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving note: {str(e)}")


@router.post("/")
async def create_note(
    request: CreateNoteRequest,
    note_manager: NoteManager = Depends(get_note_manager)
) -> Dict[str, str]:
    """
    Create a new note in the knowledge base.
    
    Args:
        request: Note creation data
        
    Returns:
        Dict containing the new note ID and status
    """
    logger.info(f"Creating note: {request.title}")
    
    try:
        note_id = note_manager.create_note(
            title=request.title,
            content=request.content,
            tags=request.tags,
            complexity=request.complexity
        )
        
        return {
            "note_id": note_id,
            "status": "created",
            "message": "Note created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating note: {str(e)}")


@router.put("/{note_id}")
async def update_note(note_id: str, request: UpdateNoteRequest) -> Dict[str, str]:
    """
    Update an existing note.
    
    Args:
        note_id: The unique identifier for the note
        request: Updated note data
        
    Returns:
        Dict containing update status
    """
    logger.info(f"Updating note: {note_id}")
    
    # TODO: Implement actual note update
    
    # Placeholder response
    return {
        "note_id": note_id,
        "status": "updated", 
        "message": "Note updated successfully"
    }


@router.delete("/{note_id}")
async def delete_note(note_id: str) -> Dict[str, str]:
    """
    Delete a note from the knowledge base.
    
    Args:
        note_id: The unique identifier for the note
        
    Returns:
        Dict containing deletion status
    """
    logger.info(f"Deleting note: {note_id}")
    
    # TODO: Implement actual note deletion with proper link cleanup
    
    # Placeholder response  
    return {
        "note_id": note_id,
        "status": "deleted",
        "message": "Note deleted successfully"
    }


@router.get("/{note_id}/links")
async def get_note_links(note_id: str) -> Dict[str, List[str]]:
    """
    Get bidirectional links for a specific note.
    
    Args:
        note_id: The unique identifier for the note
        
    Returns:
        Dict containing outgoing and incoming links
    """
    logger.info(f"Getting links for note: {note_id}")
    
    # TODO: Implement actual link retrieval from BidirectionalLinkEngine
    
    # Placeholder response
    return {
        "outgoing_links": [],
        "incoming_links": [],
        "note_id": note_id
    }


@router.post("/{note_id}/links")
async def create_link(note_id: str, target_note_id: str) -> Dict[str, str]:
    """
    Create a bidirectional link between two notes.
    
    Args:
        note_id: Source note ID
        target_note_id: Target note ID
        
    Returns:
        Dict containing link creation status
    """
    logger.info(f"Creating link: {note_id} -> {target_note_id}")
    
    # TODO: Implement actual link creation with BidirectionalLinkEngine
    
    # Placeholder response
    return {
        "status": "created",
        "message": f"Link created between {note_id} and {target_note_id}"
    }


@router.get("/{note_id}/summary")
async def get_note_summary(note_id: str) -> Dict[str, Any]:
    """
    Get an AI-generated summary of the note content.
    
    Args:
        note_id: The unique identifier for the note
        
    Returns:
        Dict containing note summary and metadata
    """
    logger.info(f"Getting summary for note: {note_id}")
    
    # TODO: Implement actual summary generation
    
    # Placeholder response
    return {
        "note_id": note_id,
        "summary": "Placeholder summary",
        "key_concepts": [],
        "generated_at": "2024-01-01T00:00:00Z"
    }