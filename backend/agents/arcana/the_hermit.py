"""
The Hermit - Path Intelligence & Context Builder Agent
MCP Capabilities: find_knowledge_paths, build_context_graph, optimize_learning_paths
Responsibility: All path intelligence and context graph construction for LLM queries
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.agents.base_agent import BaseAgent
from backend.mcp import MCPCapability, MCPCapabilityType
from backend.obsidian_vault import VaultManager, LinkGraph, PathFinder, ContextBuilder
from backend.database.repositories.knowledge_repo import KnowledgeRepository


logger = logging.getLogger(__name__)


class TheHermit(BaseAgent):
    """The Hermit - Path Intelligence & Context Builder"""
    
    def __init__(self):
        super().__init__(
            agent_id="the_hermit",
            name="The Hermit",
            description="Path intelligence specialist finding optimal knowledge connections and building context graphs"
        )
        self.vault_manager = VaultManager()
        self.link_graph = LinkGraph()
        self.path_finder = PathFinder(self.link_graph, self.vault_manager)
        self.context_builder = ContextBuilder(self.vault_manager, self.link_graph, self.path_finder)
        self.knowledge_repo = KnowledgeRepository()
        
    async def _initialize(self):
        """Initialize The Hermit agent"""
        await self.vault_manager._initialize_vault()
        await self.knowledge_repo.initialize()
        logger.info("The Hermit path intelligence systems initialized")
    
    async def _shutdown(self):
        """Shutdown The Hermit agent"""
        await self.knowledge_repo.shutdown()
        logger.info("The Hermit path intelligence systems shut down")
    
    async def _register_capabilities(self):
        """Register path intelligence capabilities"""
        self.capabilities = [
            MCPCapability(
                name="path_intelligence",
                capability_type=MCPCapabilityType.KNOWLEDGE,
                description="Advanced path finding and context graph construction using bidirectional links",
                methods={
                    "find_knowledge_paths": {
                        "description": "Find optimal paths between knowledge concepts",
                        "parameters": {
                            "start_concept": "string",
                            "target_concept": "string",
                            "max_path_length": "number"
                        }
                    },
                    "build_context_graph": {
                        "description": "Build comprehensive context graph for LLM queries",
                        "parameters": {
                            "query": "string",
                            "user_knowledge": "array",
                            "max_context_size": "number"
                        }
                    },
                    "find_shortest_paths": {
                        "description": "Find shortest paths between multiple concepts",
                        "parameters": {
                            "concepts": "array",
                            "include_intersections": "boolean"
                        }
                    },
                    "optimize_learning_path": {
                        "description": "Create optimized learning sequences based on prerequisites",
                        "parameters": {
                            "start_concept": "string",
                            "target_concept": "string",
                            "user_level": "string"
                        }
                    },
                    "analyze_knowledge_gaps": {
                        "description": "Identify gaps in user's knowledge network",
                        "parameters": {
                            "user_knowledge": "array",
                            "target_domain": "string"
                        }
                    },
                    "suggest_next_topics": {
                        "description": "Suggest next learning topics based on current knowledge",
                        "parameters": {
                            "current_knowledge": "array",
                            "limit": "number"
                        }
                    },
                    "build_learning_context": {
                        "description": "Build context optimized for learning specific topics",
                        "parameters": {
                            "topic": "string",
                            "user_level": "string",
                            "learning_objectives": "array"
                        }
                    }
                },
                agent_id=self.agent_id,
                version="2.0.0"
            )
        ]
    
    async def find_knowledge_paths(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Find optimal paths between knowledge concepts"""
        start_concept = payload.get("start_concept")
        target_concept = payload.get("target_concept")
        max_path_length = payload.get("max_path_length", 6)
        
        logger.info(f"Finding path from '{start_concept}' to '{target_concept}'")
        
        # Use path finder to create learning path
        learning_path = await self.path_finder.find_learning_path(
            start_concept, target_concept
        )
        
        if learning_path.get("error"):
            return learning_path
        
        # Enhance path with additional metadata
        enhanced_path = await self._enhance_learning_path(learning_path, max_path_length)
        
        return {
            "start_concept": start_concept,
            "target_concept": target_concept,
            "learning_path": enhanced_path,
            "path_analysis": await self._analyze_path_quality(enhanced_path),
            "estimated_learning_time": await self._estimate_learning_time(enhanced_path),
            "difficulty_progression": await self._analyze_difficulty_progression(enhanced_path)
        }
    
    async def build_context_graph(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive context graph for LLM queries"""
        query = payload.get("query")
        user_knowledge = payload.get("user_knowledge", [])
        max_context_size = payload.get("max_context_size", 20)
        
        logger.info(f"Building context graph for query: '{query}'")
        
        # Use context builder to create comprehensive context
        context_result = await self.context_builder.build_comprehensive_context(
            query=query,
            user_knowledge=user_knowledge
        )
        
        # Limit context size if requested
        if max_context_size and len(context_result["context_notes"]) > max_context_size:
            # Sort by relevance and take top notes
            sorted_notes = sorted(
                context_result["context_notes"],
                key=lambda x: x.get("combined_score", 0),
                reverse=True
            )
            context_result["context_notes"] = sorted_notes[:max_context_size]
            context_result["total_notes"] = len(context_result["context_notes"])
        
        # Add path intelligence analysis
        context_result["path_analysis"] = await self._analyze_context_paths(context_result)
        context_result["knowledge_coverage"] = await self._analyze_knowledge_coverage(
            context_result, user_knowledge
        )
        
        return context_result
    
    async def find_shortest_paths(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Find shortest paths between multiple concepts"""
        concepts = payload.get("concepts", [])
        include_intersections = payload.get("include_intersections", True)
        
        logger.info(f"Finding shortest paths between {len(concepts)} concepts")
        
        if len(concepts) < 2:
            return {"error": "At least 2 concepts required"}
        
        # Find relevant notes for each concept
        concept_notes = {}
        for concept in concepts:
            relevant = await self.path_finder.find_relevant_notes(concept, limit=2)
            if relevant:
                concept_notes[concept] = relevant[0][0]  # Take best match
        
        # Find paths between all pairs
        paths = []
        note_ids = list(concept_notes.values())
        
        for i, source in enumerate(note_ids):
            for target in note_ids[i+1:]:
                path = await self.link_graph.find_shortest_path(source, target)
                if path:
                    paths.append({
                        "source_concept": [k for k, v in concept_notes.items() if v == source][0],
                        "target_concept": [k for k, v in concept_notes.items() if v == target][0],
                        "path": path,
                        "length": len(path) - 1,
                        "path_notes": await self._get_path_metadata(path)
                    })
        
        # Find intersection points if requested
        intersections = []
        if include_intersections and len(paths) > 1:
            intersections = await self._find_path_intersections(paths)
        
        return {
            "concepts": concepts,
            "paths": paths,
            "intersections": intersections,
            "total_paths": len(paths),
            "network_analysis": await self._analyze_concept_network(concept_notes)
        }
    
    async def optimize_learning_path(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create optimized learning sequences based on prerequisites"""
        start_concept = payload.get("start_concept")
        target_concept = payload.get("target_concept")
        user_level = payload.get("user_level", "beginner")
        
        logger.info(f"Optimizing learning path from '{start_concept}' to '{target_concept}' for {user_level}")
        
        # Build basic learning path
        basic_path = await self.path_finder.find_learning_path(start_concept, target_concept)
        
        if basic_path.get("error"):
            return basic_path
        
        # Optimize based on user level and prerequisites
        optimized_path = await self._optimize_for_user_level(basic_path, user_level)
        
        # Add learning supports and scaffolding
        enhanced_path = await self._add_learning_supports(optimized_path, user_level)
        
        return {
            "start_concept": start_concept,
            "target_concept": target_concept,
            "user_level": user_level,
            "optimized_path": enhanced_path,
            "learning_strategy": await self._generate_learning_strategy(enhanced_path, user_level),
            "checkpoints": await self._identify_learning_checkpoints(enhanced_path),
            "estimated_duration": await self._estimate_learning_duration(enhanced_path, user_level)
        }
    
    async def analyze_knowledge_gaps(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Identify gaps in user's knowledge network"""
        user_knowledge = payload.get("user_knowledge", [])
        target_domain = payload.get("target_domain")
        
        logger.info(f"Analyzing knowledge gaps for domain: '{target_domain}'")
        
        # Use path finder to analyze gaps
        gap_analysis = await self.path_finder.analyze_knowledge_gaps(user_knowledge)
        
        # Focus on target domain if specified
        if target_domain:
            domain_analysis = await self._analyze_domain_gaps(user_knowledge, target_domain)
            gap_analysis["domain_specific_gaps"] = domain_analysis
        
        # Add recommendations for filling gaps
        gap_analysis["fill_recommendations"] = await self._recommend_gap_filling(
            gap_analysis, target_domain
        )
        
        return gap_analysis
    
    async def suggest_next_topics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest next learning topics based on current knowledge"""
        current_knowledge = payload.get("current_knowledge", [])
        limit = payload.get("limit", 5)
        
        logger.info(f"Suggesting next topics based on {len(current_knowledge)} known concepts")
        
        # Use path finder to suggest next topics
        suggestions = await self.path_finder.suggest_next_topics(current_knowledge, limit)
        
        # Enhance suggestions with learning readiness analysis
        enhanced_suggestions = []
        for suggestion in suggestions:
            enhanced = suggestion.copy()
            enhanced["learning_readiness"] = await self._assess_learning_readiness(
                suggestion["note_id"], current_knowledge
            )
            enhanced["learning_benefits"] = await self._analyze_learning_benefits(
                suggestion["note_id"], current_knowledge
            )
            enhanced_suggestions.append(enhanced)
        
        return {
            "current_knowledge": current_knowledge,
            "suggestions": enhanced_suggestions,
            "learning_strategy": await self._suggest_learning_strategy(enhanced_suggestions),
            "knowledge_expansion_opportunities": await self._identify_expansion_opportunities(
                current_knowledge
            )
        }
    
    async def build_learning_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Build context optimized for learning specific topics"""
        topic = payload.get("topic")
        user_level = payload.get("user_level", "beginner")
        learning_objectives = payload.get("learning_objectives", [])
        
        logger.info(f"Building learning context for topic: '{topic}' at {user_level} level")
        
        # Use context builder to create learning-optimized context
        learning_context = await self.context_builder.build_learning_context(topic, user_level)
        
        if learning_context.get("error"):
            return learning_context
        
        # Enhance with learning objectives
        if learning_objectives:
            learning_context["objective_alignment"] = await self._align_with_objectives(
                learning_context, learning_objectives
            )
        
        # Add pedagogical enhancements
        learning_context["pedagogical_structure"] = await self._create_pedagogical_structure(
            learning_context, user_level
        )
        
        return learning_context
    
    # Helper methods
    
    async def _enhance_learning_path(self, learning_path: Dict[str, Any], max_length: int) -> Dict[str, Any]:
        """Enhance learning path with additional metadata"""
        if not learning_path.get("path"):
            return learning_path
        
        enhanced_path = learning_path.copy()
        
        # Add prerequisite analysis for each step
        for step in enhanced_path["path"]:
            step["prerequisite_coverage"] = await self._check_prerequisite_coverage(
                step["note_id"], enhanced_path["path"]
            )
            step["cognitive_load"] = await self._estimate_cognitive_load(step["note_id"])
        
        return enhanced_path
    
    async def _analyze_path_quality(self, learning_path: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality of a learning path"""
        if not learning_path.get("path"):
            return {"quality_score": 0}
        
        path_steps = learning_path["path"]
        
        # Calculate various quality metrics
        difficulty_smoothness = await self._calculate_difficulty_smoothness(path_steps)
        prerequisite_coverage = await self._calculate_prerequisite_coverage(path_steps)
        concept_coherence = await self._calculate_concept_coherence(path_steps)
        
        quality_score = (difficulty_smoothness + prerequisite_coverage + concept_coherence) / 3
        
        return {
            "quality_score": quality_score,
            "difficulty_smoothness": difficulty_smoothness,
            "prerequisite_coverage": prerequisite_coverage,
            "concept_coherence": concept_coherence,
            "recommendations": await self._generate_path_improvements(path_steps, quality_score)
        }
    
    async def _estimate_learning_time(self, learning_path: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate time required to complete learning path"""
        if not learning_path.get("path"):
            return {"total_hours": 0}
        
        total_hours = 0
        step_estimates = []
        
        for step in learning_path["path"]:
            difficulty = step.get("difficulty", 0.5)
            # Base time: 1-4 hours per concept based on difficulty
            step_time = 1 + (difficulty * 3)
            total_hours += step_time
            
            step_estimates.append({
                "step": step["title"],
                "estimated_hours": step_time,
                "factors": {
                    "difficulty": difficulty,
                    "concept_density": await self._calculate_concept_density(step["note_id"])
                }
            })
        
        return {
            "total_hours": total_hours,
            "step_estimates": step_estimates,
            "daily_plan": await self._create_daily_plan(step_estimates)
        }
    
    async def _analyze_difficulty_progression(self, learning_path: Dict[str, Any]) -> List[float]:
        """Analyze difficulty progression through learning path"""
        if not learning_path.get("path"):
            return []
        
        difficulties = []
        for step in learning_path["path"]:
            difficulties.append(step.get("difficulty", 0.5))
        
        return difficulties
    
    async def _analyze_context_paths(self, context_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the paths within a context graph"""
        paths = context_result.get("connection_paths", [])
        
        if not paths:
            return {"path_count": 0}
        
        return {
            "path_count": len(paths),
            "average_path_length": sum(p["length"] for p in paths) / len(paths),
            "shortest_path": min(paths, key=lambda x: x["length"]),
            "longest_path": max(paths, key=lambda x: x["length"]),
            "path_diversity": len(set(tuple(p["path"]) for p in paths)) / len(paths)
        }
    
    async def _analyze_knowledge_coverage(self, context_result: Dict[str, Any], user_knowledge: List[str]) -> Dict[str, Any]:
        """Analyze how well the context covers user's knowledge needs"""
        context_notes = context_result.get("context_notes", [])
        
        if not context_notes:
            return {"coverage_score": 0}
        
        # Calculate coverage metrics
        total_concepts = len(context_notes)
        primary_concepts = len([n for n in context_notes if n.get("is_primary", False)])
        bridging_concepts = total_concepts - primary_concepts
        
        coverage_score = min(primary_concepts / max(len(user_knowledge), 1), 1.0)
        
        return {
            "coverage_score": coverage_score,
            "total_concepts": total_concepts,
            "primary_concepts": primary_concepts,
            "bridging_concepts": bridging_concepts,
            "knowledge_density": total_concepts / max(len(user_knowledge), 1)
        }
    
    async def _get_path_metadata(self, path: List[str]) -> List[Dict[str, Any]]:
        """Get metadata for notes in a path"""
        path_metadata = []
        
        for note_id in path:
            note_data = self.vault_manager.note_index.get(note_id)
            if note_data:
                path_metadata.append({
                    "note_id": note_id,
                    "title": note_data.get("title", ""),
                    "difficulty": note_data.get("frontmatter", {}).get("difficulty", 0.5),
                    "tags": note_data.get("frontmatter", {}).get("tags", [])
                })
        
        return path_metadata
    
    async def _find_path_intersections(self, paths: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find intersection points between multiple paths"""
        # Count frequency of each node across all paths
        node_frequency = {}
        
        for path_info in paths:
            for node in path_info["path"]:
                node_frequency[node] = node_frequency.get(node, 0) + 1
        
        # Find nodes that appear in multiple paths
        intersections = []
        for node, frequency in node_frequency.items():
            if frequency > 1:
                note_data = self.vault_manager.note_index.get(node)
                if note_data:
                    intersections.append({
                        "note_id": node,
                        "title": note_data.get("title", ""),
                        "frequency": frequency,
                        "importance_score": frequency / len(paths)
                    })
        
        # Sort by importance
        intersections.sort(key=lambda x: x["importance_score"], reverse=True)
        
        return intersections
    
    async def _analyze_concept_network(self, concept_notes: Dict[str, str]) -> Dict[str, Any]:
        """Analyze the network structure of concepts"""
        if len(concept_notes) < 2:
            return {"network_density": 0}
        
        # Calculate network metrics
        total_possible_connections = len(concept_notes) * (len(concept_notes) - 1) / 2
        actual_connections = 0
        
        note_ids = list(concept_notes.values())
        for i, source in enumerate(note_ids):
            for target in note_ids[i+1:]:
                if await self.link_graph.has_path(source, target):
                    actual_connections += 1
        
        network_density = actual_connections / total_possible_connections if total_possible_connections > 0 else 0
        
        return {
            "network_density": network_density,
            "total_concepts": len(concept_notes),
            "total_connections": actual_connections,
            "connectivity_score": min(network_density * 2, 1.0)  # Normalize to 0-1
        }
    
    # Additional helper methods would continue here...
    # (For brevity, I'll implement key methods and leave placeholders for others)
    
    async def _optimize_for_user_level(self, basic_path: Dict[str, Any], user_level: str) -> Dict[str, Any]:
        """Optimize path based on user level"""
        # Placeholder - would implement user level optimization
        return basic_path
    
    async def _add_learning_supports(self, path: Dict[str, Any], user_level: str) -> Dict[str, Any]:
        """Add learning supports and scaffolding"""
        # Placeholder - would add scaffolding based on user level
        return path
    
    async def _generate_learning_strategy(self, path: Dict[str, Any], user_level: str) -> Dict[str, Any]:
        """Generate learning strategy for the path"""
        return {
            "approach": "progressive",
            "time_management": "spaced_practice",
            "review_frequency": "daily" if user_level == "beginner" else "weekly"
        }
    
    async def _identify_learning_checkpoints(self, path: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify key learning checkpoints"""
        # Placeholder - would identify key checkpoints
        return []
    
    async def _estimate_learning_duration(self, path: Dict[str, Any], user_level: str) -> Dict[str, Any]:
        """Estimate total learning duration"""
        base_hours = len(path.get("path", [])) * 2
        multiplier = {"beginner": 1.5, "intermediate": 1.0, "advanced": 0.7}.get(user_level, 1.0)
        
        return {
            "total_hours": base_hours * multiplier,
            "recommended_daily_hours": 1 if user_level == "beginner" else 2,
            "estimated_weeks": (base_hours * multiplier) / (7 * (1 if user_level == "beginner" else 2))
        }
    
    # More placeholder methods...
    async def _analyze_domain_gaps(self, user_knowledge: List[str], domain: str) -> Dict[str, Any]:
        return {"domain_gaps": [], "coverage_percentage": 0.7}
    
    async def _recommend_gap_filling(self, gap_analysis: Dict[str, Any], domain: str) -> List[str]:
        return ["Focus on fundamental concepts", "Build connecting knowledge"]
    
    async def _assess_learning_readiness(self, note_id: str, current_knowledge: List[str]) -> float:
        return 0.8  # Placeholder readiness score
    
    async def _analyze_learning_benefits(self, note_id: str, current_knowledge: List[str]) -> Dict[str, Any]:
        return {"knowledge_expansion": 0.7, "skill_application": 0.6}
    
    async def _suggest_learning_strategy(self, suggestions: List[Dict[str, Any]]) -> Dict[str, str]:
        return {"approach": "sequential", "focus": "conceptual_understanding"}
    
    async def _identify_expansion_opportunities(self, current_knowledge: List[str]) -> List[Dict[str, Any]]:
        return [{"opportunity": "advanced_applications", "potential": 0.8}]
    
    async def _align_with_objectives(self, context: Dict[str, Any], objectives: List[str]) -> Dict[str, Any]:
        return {"alignment_score": 0.85, "missing_objectives": []}
    
    async def _create_pedagogical_structure(self, context: Dict[str, Any], user_level: str) -> Dict[str, Any]:
        return {"structure": "scaffolded", "supports": ["examples", "practice"]}
    
    async def _check_prerequisite_coverage(self, note_id: str, path_steps: List[Dict[str, Any]]) -> float:
        return 0.9  # Placeholder coverage score
    
    async def _estimate_cognitive_load(self, note_id: str) -> float:
        return 0.6  # Placeholder cognitive load
    
    async def _calculate_difficulty_smoothness(self, path_steps: List[Dict[str, Any]]) -> float:
        return 0.8  # Placeholder smoothness score
    
    async def _calculate_prerequisite_coverage(self, path_steps: List[Dict[str, Any]]) -> float:
        return 0.85  # Placeholder coverage
    
    async def _calculate_concept_coherence(self, path_steps: List[Dict[str, Any]]) -> float:
        return 0.75  # Placeholder coherence
    
    async def _generate_path_improvements(self, path_steps: List[Dict[str, Any]], quality_score: float) -> List[str]:
        improvements = []
        if quality_score < 0.7:
            improvements.append("Add intermediate concepts to smooth difficulty progression")
        if quality_score < 0.5:
            improvements.append("Consider alternative learning sequence")
        return improvements
    
    async def _calculate_concept_density(self, note_id: str) -> float:
        return 0.6  # Placeholder concept density
    
    async def _create_daily_plan(self, step_estimates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [{"day": 1, "topics": ["Introduction"], "hours": 2}]  # Placeholder daily plan