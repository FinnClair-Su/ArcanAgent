"""
Vector Store for GRAG
Manages vector embeddings and similarity search
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
import faiss

from backend.settings import settings


logger = logging.getLogger(__name__)


class VectorStore:
    """Vector store for concept embeddings"""
    
    def __init__(self):
        self.model = None
        self.index = None
        self.concept_ids = []
        self.concept_metadata = {}
    
    async def initialize(self):
        """Initialize vector store"""
        logger.info("Initializing vector store...")
        
        # Load embedding model
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(settings.VECTOR_DIMENSION)
        
        logger.info("Vector store initialized")
    
    async def shutdown(self):
        """Shutdown vector store"""
        logger.info("Vector store shut down")
    
    async def add_concept(self, concept_id: str, concept: Dict[str, Any]):
        """Add concept to vector store"""
        # Create text representation
        text = f"{concept.get('name', '')} {concept.get('description', '')}"
        
        # Generate embedding
        embedding = self.model.encode([text])
        
        # Add to index
        self.index.add(embedding.astype(np.float32))
        
        # Store metadata
        self.concept_ids.append(concept_id)
        self.concept_metadata[concept_id] = concept
        
        logger.debug(f"Added concept to vector store: {concept_id}")
    
    async def search_similar(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """Search for similar concepts"""
        if not self.model or not self.index:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query])
        
        # Search index
        scores, indices = self.index.search(query_embedding.astype(np.float32), k)
        
        # Return results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.concept_ids):
                concept_id = self.concept_ids[idx]
                score = scores[0][i]
                results.append((concept_id, float(score)))
        
        return results
    
    async def get_size(self) -> int:
        """Get number of concepts in vector store"""
        return len(self.concept_ids)