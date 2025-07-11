"""
Concept Linker for GRAG
Links extracted concepts to knowledge graph
"""

import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class ConceptLinker:
    """Links concepts to knowledge graph"""
    
    def __init__(self, grag_engine):
        self.grag_engine = grag_engine
    
    async def link_concept(self, triple: Tuple[str, str, str]) -> Optional[Dict[str, Any]]:
        """Link concept from triple"""
        subject, relation, object_ = triple
        
        # Try to find existing concepts
        subject_concept = await self._find_or_create_concept(subject)
        object_concept = await self._find_or_create_concept(object_)
        
        # Create relation
        if subject_concept and object_concept:
            relation_id = await self.grag_engine.add_relation(
                subject_concept['id'],
                object_concept['id'],
                relation
            )
            
            return {
                "subject": subject_concept,
                "relation": relation,
                "object": object_concept,
                "relation_id": relation_id
            }
        
        return None
    
    async def _find_or_create_concept(self, concept_name: str) -> Optional[Dict[str, Any]]:
        """Find or create concept"""
        # Search for existing concept
        search_results = await self.grag_engine.search_concepts(concept_name, 1)
        
        if search_results:
            return search_results[0]['concept']
        
        # Create new concept
        concept_id = await self.grag_engine.add_concept({
            "name": concept_name,
            "description": f"Auto-generated concept: {concept_name}",
            "domain": "general"
        })
        
        return await self.grag_engine.get_concept(concept_id)