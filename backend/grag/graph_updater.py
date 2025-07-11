"""
Graph Updater for GRAG
Handles incremental updates to knowledge graph
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class GraphUpdater:
    """Handles knowledge graph updates"""
    
    def __init__(self, grag_engine):
        self.grag_engine = grag_engine
    
    async def update_graph(self, data: Dict[str, Any]):
        """Update knowledge graph with new data"""
        update_type = data.get('type', 'unknown')
        
        if update_type == 'concept':
            await self._update_concept(data)
        elif update_type == 'relation':
            await self._update_relation(data)
        elif update_type == 'user_knowledge':
            await self._update_user_knowledge(data)
        else:
            logger.warning(f"Unknown update type: {update_type}")
    
    async def _update_concept(self, data: Dict[str, Any]):
        """Update concept"""
        concept_id = data.get('concept_id')
        if concept_id:
            await self.grag_engine.add_concept(data)
    
    async def _update_relation(self, data: Dict[str, Any]):
        """Update relation"""
        source_id = data.get('source_id')
        target_id = data.get('target_id')
        relation_type = data.get('relation_type')
        
        if source_id and target_id and relation_type:
            await self.grag_engine.add_relation(source_id, target_id, relation_type)
    
    async def _update_user_knowledge(self, data: Dict[str, Any]):
        """Update user knowledge"""
        user_id = data.get('user_id')
        concept_id = data.get('concept_id')
        knowledge_level = data.get('knowledge_level')
        
        if user_id and concept_id and knowledge_level is not None:
            await self.grag_engine.update_user_knowledge(user_id, concept_id, knowledge_level)