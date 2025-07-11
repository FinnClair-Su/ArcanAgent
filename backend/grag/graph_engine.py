"""
GRAG Graph Engine
Core knowledge graph management system
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from neo4j import GraphDatabase, Session
from neo4j.exceptions import ServiceUnavailable

from backend.settings import settings
from .vector_store import VectorStore
from .hybrid_search import HybridSearch
from .triple_extractor import TripleExtractor
from .concept_linker import ConceptLinker
from .graph_updater import GraphUpdater


logger = logging.getLogger(__name__)


class GRAGEngine:
    """GRAG knowledge graph engine"""
    
    def __init__(self):
        self.driver = None
        self.vector_store = VectorStore()
        self.hybrid_search = HybridSearch(self)
        self.triple_extractor = TripleExtractor()
        self.concept_linker = ConceptLinker(self)
        self.graph_updater = GraphUpdater(self)
        
    async def initialize(self):
        """Initialize GRAG engine"""
        logger.info("Initializing GRAG engine...")
        
        # Connect to Neo4j
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
        
        # Test connection
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Connected to Neo4j successfully")
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
        
        # Initialize vector store
        await self.vector_store.initialize()
        
        # Create graph constraints and indexes
        await self._create_constraints()
        await self._create_indexes()
        
        logger.info("GRAG engine initialized successfully")
    
    async def shutdown(self):
        """Shutdown GRAG engine"""
        if self.driver:
            self.driver.close()
        await self.vector_store.shutdown()
        logger.info("GRAG engine shut down")
    
    async def _create_constraints(self):
        """Create graph constraints"""
        constraints = [
            "CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT relation_id IF NOT EXISTS FOR (r:Relation) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
            "CREATE CONSTRAINT session_id IF NOT EXISTS FOR (s:Session) REQUIRE s.id IS UNIQUE",
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    logger.warning(f"Constraint creation failed: {e}")
    
    async def _create_indexes(self):
        """Create graph indexes"""
        indexes = [
            "CREATE INDEX concept_name IF NOT EXISTS FOR (c:Concept) ON (c.name)",
            "CREATE INDEX concept_domain IF NOT EXISTS FOR (c:Concept) ON (c.domain)",
            "CREATE INDEX relation_type IF NOT EXISTS FOR (r:Relation) ON (r.type)",
            "CREATE INDEX user_name IF NOT EXISTS FOR (u:User) ON (u.name)",
        ]
        
        with self.driver.session() as session:
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    logger.warning(f"Index creation failed: {e}")
    
    def get_session(self) -> Session:
        """Get Neo4j session"""
        return self.driver.session()
    
    async def add_concept(self, concept: Dict[str, Any]) -> str:
        """Add concept to knowledge graph"""
        concept_id = concept.get("id") or f"concept_{len(await self.get_all_concepts())}"
        
        with self.get_session() as session:
            result = session.run(
                """
                MERGE (c:Concept {id: $id})
                SET c.name = $name,
                    c.description = $description,
                    c.domain = $domain,
                    c.difficulty = $difficulty,
                    c.created_at = datetime(),
                    c.updated_at = datetime()
                RETURN c.id as id
                """,
                id=concept_id,
                name=concept.get("name", ""),
                description=concept.get("description", ""),
                domain=concept.get("domain", "general"),
                difficulty=concept.get("difficulty", 1.0)
            )
        
        # Add to vector store
        await self.vector_store.add_concept(concept_id, concept)
        
        logger.info(f"Added concept: {concept_id}")
        return concept_id
    
    async def add_relation(self, source_id: str, target_id: str, relation_type: str, properties: Dict[str, Any] = None) -> str:
        """Add relation between concepts"""
        relation_id = f"rel_{source_id}_{target_id}_{relation_type}"
        properties = properties or {}
        
        with self.get_session() as session:
            session.run(
                """
                MATCH (s:Concept {id: $source_id})
                MATCH (t:Concept {id: $target_id})
                MERGE (s)-[r:RELATES {id: $relation_id, type: $type}]->(t)
                SET r.strength = $strength,
                    r.created_at = datetime(),
                    r.updated_at = datetime()
                """,
                source_id=source_id,
                target_id=target_id,
                relation_id=relation_id,
                type=relation_type,
                strength=properties.get("strength", 1.0)
            )
        
        logger.info(f"Added relation: {relation_id}")
        return relation_id
    
    async def get_concept(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Get concept by ID"""
        with self.get_session() as session:
            result = session.run(
                """
                MATCH (c:Concept {id: $id})
                RETURN c
                """,
                id=concept_id
            )
            
            record = result.single()
            if record:
                return dict(record["c"])
            return None
    
    async def get_all_concepts(self) -> List[Dict[str, Any]]:
        """Get all concepts"""
        with self.get_session() as session:
            result = session.run("MATCH (c:Concept) RETURN c")
            return [dict(record["c"]) for record in result]
    
    async def get_concept_relations(self, concept_id: str) -> List[Dict[str, Any]]:
        """Get relations for a concept"""
        with self.get_session() as session:
            result = session.run(
                """
                MATCH (c:Concept {id: $id})-[r:RELATES]->(t:Concept)
                RETURN r, t
                UNION
                MATCH (s:Concept)-[r:RELATES]->(c:Concept {id: $id})
                RETURN r, s as t
                """,
                id=concept_id
            )
            
            relations = []
            for record in result:
                relations.append({
                    "relation": dict(record["r"]),
                    "target": dict(record["t"])
                })
            
            return relations
    
    async def find_learning_path(self, start_concept: str, end_concept: str) -> List[str]:
        """Find learning path between concepts"""
        with self.get_session() as session:
            result = session.run(
                """
                MATCH path = shortestPath((start:Concept {id: $start})-[:RELATES*]->(end:Concept {id: $end}))
                RETURN [node in nodes(path) | node.id] as path
                """,
                start=start_concept,
                end=end_concept
            )
            
            record = result.single()
            if record:
                return record["path"]
            return []
    
    async def get_concept_dependencies(self, concept_id: str) -> List[str]:
        """Get concept dependencies (prerequisites)"""
        with self.get_session() as session:
            result = session.run(
                """
                MATCH (prereq:Concept)-[:RELATES {type: 'prerequisite'}]->(c:Concept {id: $id})
                RETURN prereq.id as id
                """,
                id=concept_id
            )
            
            return [record["id"] for record in result]
    
    async def update_user_knowledge(self, user_id: str, concept_id: str, knowledge_level: float):
        """Update user's knowledge level for a concept"""
        with self.get_session() as session:
            session.run(
                """
                MERGE (u:User {id: $user_id})
                MERGE (c:Concept {id: $concept_id})
                MERGE (u)-[k:KNOWS]->(c)
                SET k.level = $level,
                    k.updated_at = datetime()
                """,
                user_id=user_id,
                concept_id=concept_id,
                level=knowledge_level
            )
    
    async def get_user_knowledge(self, user_id: str) -> Dict[str, float]:
        """Get user's knowledge levels"""
        with self.get_session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[k:KNOWS]->(c:Concept)
                RETURN c.id as concept_id, k.level as level
                """,
                user_id=user_id
            )
            
            return {record["concept_id"]: record["level"] for record in result}
    
    async def get_recommended_concepts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recommended concepts for user"""
        with self.get_session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[k:KNOWS]->(known:Concept)
                MATCH (known)-[:RELATES {type: 'leads_to'}]->(next:Concept)
                WHERE NOT EXISTS((u)-[:KNOWS]->(next))
                RETURN next, AVG(k.level) as readiness
                ORDER BY readiness DESC
                LIMIT $limit
                """,
                user_id=user_id,
                limit=limit
            )
            
            return [
                {
                    "concept": dict(record["next"]),
                    "readiness": record["readiness"]
                }
                for record in result
            ]
    
    async def search_concepts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search concepts using hybrid search"""
        return await self.hybrid_search.search(query, limit)
    
    async def extract_and_link_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Extract and link concepts from text"""
        # Extract triples
        triples = await self.triple_extractor.extract_triples(text)
        
        # Link concepts
        linked_concepts = []
        for triple in triples:
            concept = await self.concept_linker.link_concept(triple)
            if concept:
                linked_concepts.append(concept)
        
        return linked_concepts
    
    async def update_knowledge_graph(self, data: Dict[str, Any]):
        """Update knowledge graph with new data"""
        await self.graph_updater.update_graph(data)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        with self.get_session() as session:
            result = session.run(
                """
                MATCH (c:Concept)
                OPTIONAL MATCH (c)-[r:RELATES]->()
                RETURN COUNT(DISTINCT c) as concepts,
                       COUNT(r) as relations
                """
            )
            
            record = result.single()
            return {
                "concepts": record["concepts"],
                "relations": record["relations"],
                "vector_store_size": await self.vector_store.get_size()
            }