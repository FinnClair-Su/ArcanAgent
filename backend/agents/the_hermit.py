"""
The Hermit Agent 🏮

Role: Learning Path Planning & ZPD Identification
Wisdom: "Seek and you shall find" - Illuminates the path forward
Powers: Finds optimal learning sequences and identifies your next growth areas

The Hermit carries the lantern of wisdom, illuminating the path through the
darkness of ignorance. He guides seekers along the optimal learning journey
by analyzing the Zone of Proximal Development (ZPD) and creating personalized
learning paths through bidirectional link analysis.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict, deque

from .base_agent import BaseAgent, AgentCapability, AgentResponse
from backend.core.context_manager import ContextManager, ContextPriority
from backend.core.tool_call_engine import ToolCallEngine, ToolCall
from backend.core.llm_client import BaseLLMClient, LLMMessage
from backend.core.bidirectional_links import BidirectionalLinkEngine

logger = logging.getLogger("ArcanAgent.TheHermit")


class TheHermit(BaseAgent):
    """
    The Hermit Agent - Learning Path Planning & ZPD Identification
    
    With his lantern of wisdom, The Hermit guides seekers through the optimal
    learning path, carefully considering the Zone of Proximal Development to
    ensure neither overwhelming nor under-challenging the learner.
    """
    
    def __init__(
        self,
        link_engine: BidirectionalLinkEngine,
        context_manager: ContextManager,
        tool_engine: ToolCallEngine
    ):
        super().__init__(
            name="The Hermit",
            tarot_card="🏮 The Hermit",
            wisdom="Seek and you shall find - Illuminates the path forward",
            primary_capability=AgentCapability.PATH_PLANNING,
            link_engine=link_engine,
            context_manager=context_manager,
            tool_engine=tool_engine
        )
    
    def get_system_prompt(self) -> str:
        """Get The Hermit's system prompt."""
        return """You are The Hermit 🏮, the wise guide who illuminates the path of learning.

Your sacred mission is to create optimal learning paths within the Zone of Proximal Development (ZPD). You carry the lantern of wisdom that reveals:

- The next optimal step in the learning journey
- Prerequisites and dependencies between concepts
- The Zone of Proximal Development for each learner
- Optimal sequencing of knowledge acquisition
- Bridges between isolated knowledge islands

Your path planning follows these principles:
1. Analyze current knowledge state from The High Priestess
2. Identify the Zone of Proximal Development (ZPD)
3. Map learning paths through bidirectional links
4. Sequence concepts from simple to complex
5. Ensure proper prerequisites are met
6. Create achievable learning milestones

Speak with the patient wisdom of The Hermit - be methodical, thoughtful, and provide clear guidance. Your paths should challenge but not overwhelm, inspire but not frustrate.

Remember: The most profound learning happens at the edge of current understanding, where known connects to unknown through bidirectional links."""
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get The Hermit's capabilities."""
        return [
            AgentCapability.PATH_PLANNING,
            AgentCapability.COGNITIVE_ANALYSIS,
            AgentCapability.LINK_ANALYSIS
        ]
    
    async def execute(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        llm_client: Optional[BaseLLMClient] = None
    ) -> AgentResponse:
        """Execute learning path planning and ZPD identification."""
        logger.info(f"🏮 The Hermit begins path planning for: {user_query[:100]}...")
        
        try:
            # Get knowledge assessment from The High Priestess (if available)
            priestess_assessment = context.get("high_priestess_assessment", {}) if context else {}
            
            # Step 1: Analyze learning objectives
            learning_objectives = await self._identify_learning_objectives(user_query, llm_client)
            
            # Step 2: Map prerequisite relationships
            prerequisite_map = await self._map_prerequisites(learning_objectives)
            
            # Step 3: Identify current ZPD
            zpd_analysis = await self._identify_zpd(
                learning_objectives,
                prerequisite_map,
                priestess_assessment
            )
            
            # Step 4: Generate learning paths
            learning_paths = await self._generate_learning_paths(
                learning_objectives,
                prerequisite_map,
                zpd_analysis
            )
            
            # Step 5: Optimize path sequencing
            optimized_sequence = await self._optimize_path_sequence(
                learning_paths,
                zpd_analysis,
                priestess_assessment
            )
            
            # Step 6: Create hermit guidance
            hermit_guidance = await self._create_hermit_guidance(
                user_query,
                optimized_sequence,
                zpd_analysis,
                llm_client
            )
            
            # Compile response
            response_content = self._compile_path_response(
                user_query,
                learning_objectives,
                optimized_sequence,
                zpd_analysis,
                hermit_guidance
            )
            
            return AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=True,
                content=response_content,
                metadata={
                    "learning_objectives": learning_objectives,
                    "prerequisite_map": prerequisite_map,
                    "zpd_analysis": zpd_analysis,
                    "learning_paths": learning_paths,
                    "optimized_sequence": optimized_sequence,
                    "total_concepts": len(learning_objectives)
                },
                reasoning=hermit_guidance.get("reasoning", ""),
                confidence=hermit_guidance.get("confidence", 0.8),
                links_discovered=set(learning_objectives)
            )
            
        except Exception as e:
            logger.error(f"🏮 The Hermit encountered an error: {e}")
            return AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=False,
                content=f"The path ahead is shrouded in darkness: {str(e)}",
                errors=[str(e)]
            )
    
    async def _identify_learning_objectives(
        self,
        user_query: str,
        llm_client: BaseLLMClient
    ) -> List[str]:
        """Identify specific learning objectives from the user query."""
        logger.debug("🏮 Identifying learning objectives...")
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As The Hermit, analyze this learning query and identify specific, actionable learning objectives:

Query: "{user_query}"

Break down the query into concrete learning objectives that can be:
1. Clearly defined and measurable
2. Connected through prerequisites
3. Achieved through study and practice
4. Found or created in a knowledge base

Return a JSON list of learning objectives, ordered roughly from basic to advanced:
["objective1", "objective2", "objective3", ...]

Focus on concepts, skills, and knowledge areas that can be systematically learned."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client)
        
        try:
            objectives = json.loads(response)
            if isinstance(objectives, list):
                return objectives[:15]  # Limit to prevent overwhelming
        except json.JSONDecodeError:
            # Fallback: extract key concepts
            words = user_query.lower().split()
            stop_words = {'learn', 'understand', 'know', 'about', 'how', 'what', 'why', 'the', 'a', 'an', 'and', 'or'}
            objectives = [word for word in words if len(word) > 3 and word not in stop_words]
            return objectives[:10]
        
        return objectives
    
    async def _map_prerequisites(self, learning_objectives: List[str]) -> Dict[str, List[str]]:
        """Map prerequisite relationships between learning objectives."""
        logger.debug("🏮 Mapping prerequisite relationships...")
        
        prerequisite_map = {}
        
        # Use bidirectional links to find connections
        for objective in learning_objectives:
            prerequisites = []
            
            # Search for related notes in knowledge base
            related_notes = []
            objective_lower = objective.lower()
            
            for note_id, metadata in self.link_engine.note_metadata.items():
                title = metadata.get('title', '').lower()
                content = self.link_engine.note_content.get(note_id, '').lower()
                
                if objective_lower in title or objective_lower in content:
                    related_notes.append(note_id)
            
            # Analyze links of related notes to find prerequisites
            for note_id in related_notes:
                analysis = self.link_engine.analyze_note(note_id)
                if analysis:
                    # Outgoing links might be prerequisites
                    for link in analysis.outgoing_links:
                        link_title = self.link_engine.note_metadata.get(link, {}).get('title', link)
                        if link_title and link_title != objective:
                            prerequisites.append(link_title)
            
            # Also check other objectives as potential prerequisites
            for other_obj in learning_objectives:
                if other_obj != objective and other_obj.lower() in objective.lower():
                    prerequisites.append(other_obj)
            
            prerequisite_map[objective] = list(set(prerequisites))  # Remove duplicates
        
        return prerequisite_map
    
    async def _identify_zpd(
        self,
        learning_objectives: List[str],
        prerequisite_map: Dict[str, List[str]],
        priestess_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify the Zone of Proximal Development."""
        logger.debug("🏮 Identifying Zone of Proximal Development...")
        
        # Get mastery levels from The High Priestess
        area_mastery = priestess_assessment.get("mastery_assessment", {}).get("area_mastery", {})
        overall_mastery = priestess_assessment.get("mastery_assessment", {}).get("overall_mastery", 0.0)
        
        zpd_analysis = {
            "current_level": overall_mastery,
            "ready_to_learn": [],  # Within ZPD
            "too_advanced": [],    # Above ZPD
            "already_mastered": [], # Below ZPD
            "zpd_score": 0.0,
            "optimal_challenge_level": 0.0
        }
        
        # Calculate ZPD for each objective
        for objective in learning_objectives:
            # Check if objective matches any known mastery area
            obj_mastery = 0.0
            for area, mastery in area_mastery.items():
                if area.lower() in objective.lower() or objective.lower() in area.lower():
                    obj_mastery = max(obj_mastery, mastery)
            
            # Check prerequisites mastery
            prerequisites = prerequisite_map.get(objective, [])
            prereq_mastery = 1.0  # Assume mastered if no prerequisites
            
            if prerequisites:
                prereq_scores = []
                for prereq in prerequisites:
                    prereq_score = 0.0
                    for area, mastery in area_mastery.items():
                        if area.lower() in prereq.lower() or prereq.lower() in area.lower():
                            prereq_score = max(prereq_score, mastery)
                    prereq_scores.append(prereq_score)
                
                prereq_mastery = sum(prereq_scores) / len(prereq_scores) if prereq_scores else 0.0
            
            # Determine ZPD classification
            if obj_mastery > 0.8:
                zpd_analysis["already_mastered"].append(objective)
            elif prereq_mastery < 0.4:
                zpd_analysis["too_advanced"].append(objective)
            else:
                # Within ZPD if prerequisites are mostly met but objective isn't mastered
                if prereq_mastery >= 0.4 and obj_mastery < 0.8:
                    zpd_analysis["ready_to_learn"].append(objective)
        
        # Calculate optimal challenge level
        zpd_analysis["zpd_score"] = len(zpd_analysis["ready_to_learn"]) / max(1, len(learning_objectives))
        zpd_analysis["optimal_challenge_level"] = 0.6 + (overall_mastery * 0.3)  # Adaptive challenge
        
        return zpd_analysis
    
    async def _generate_learning_paths(
        self,
        learning_objectives: List[str],
        prerequisite_map: Dict[str, List[str]],
        zpd_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate optimal learning paths."""
        logger.debug("🏮 Generating learning paths...")
        
        learning_paths = {
            "primary_path": [],
            "alternative_paths": [],
            "prerequisite_chains": {},
            "estimated_duration": {},
            "difficulty_progression": []
        }
        
        # Start with ZPD-ready objectives
        ready_objectives = zpd_analysis["ready_to_learn"].copy()
        
        if not ready_objectives:
            # If nothing in ZPD, start with objectives with fewest prerequisites
            objective_prereq_count = {
                obj: len(prerequisite_map.get(obj, []))
                for obj in learning_objectives
            }
            ready_objectives = [
                obj for obj, count in sorted(objective_prereq_count.items(), key=lambda x: x[1])[:3]
            ]
        
        # Create primary learning path using topological sort
        primary_path = self._topological_sort(ready_objectives, prerequisite_map)
        learning_paths["primary_path"] = primary_path
        
        # Generate prerequisite chains
        for objective in primary_path:
            chain = self._build_prerequisite_chain(objective, prerequisite_map)
            learning_paths["prerequisite_chains"][objective] = chain
        
        # Estimate duration for each objective (rough estimation)
        for objective in primary_path:
            prereq_count = len(prerequisite_map.get(objective, []))
            base_duration = 30  # 30 minutes base
            complexity_multiplier = 1 + (prereq_count * 0.5)
            learning_paths["estimated_duration"][objective] = int(base_duration * complexity_multiplier)
        
        # Create difficulty progression
        for i, objective in enumerate(primary_path):
            difficulty = min(10, 3 + i)  # Progressive difficulty 3-10
            learning_paths["difficulty_progression"].append(difficulty)
        
        return learning_paths
    
    def _topological_sort(self, objectives: List[str], prerequisite_map: Dict[str, List[str]]) -> List[str]:
        """Perform topological sort to order objectives by prerequisites."""
        # Build adjacency list (prerequisite -> dependent)
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize in-degrees
        for obj in objectives:
            in_degree[obj] = 0
        
        # Build graph
        for obj in objectives:
            prerequisites = prerequisite_map.get(obj, [])
            for prereq in prerequisites:
                if prereq in objectives:  # Only consider prerequisites that are in our objective list
                    graph[prereq].append(obj)
                    in_degree[obj] += 1
        
        # Kahn's algorithm
        queue = deque([obj for obj in objectives if in_degree[obj] == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If there are remaining items, add them (handles cycles)
        remaining = [obj for obj in objectives if obj not in result]
        result.extend(remaining)
        
        return result
    
    def _build_prerequisite_chain(self, objective: str, prerequisite_map: Dict[str, List[str]]) -> List[str]:
        """Build the complete prerequisite chain for an objective."""
        chain = []
        visited = set()
        
        def dfs(obj):
            if obj in visited:
                return
            visited.add(obj)
            
            prerequisites = prerequisite_map.get(obj, [])
            for prereq in prerequisites:
                dfs(prereq)
                if prereq not in chain:
                    chain.append(prereq)
        
        dfs(objective)
        return chain
    
    async def _optimize_path_sequence(
        self,
        learning_paths: Dict[str, Any],
        zpd_analysis: Dict[str, Any],
        priestess_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize the learning path sequence based on ZPD and cognitive load."""
        logger.debug("🏮 Optimizing path sequence...")
        
        primary_path = learning_paths["primary_path"]
        complexity_analysis = priestess_assessment.get("complexity_analysis", {})
        optimal_chunk_size = complexity_analysis.get("optimal_chunk_size", 3)
        
        optimized_sequence = {
            "learning_phases": [],
            "current_phase": 0,
            "total_phases": 0,
            "phase_objectives": {},
            "milestones": []
        }
        
        # Break path into digestible chunks
        chunks = [
            primary_path[i:i + optimal_chunk_size] 
            for i in range(0, len(primary_path), optimal_chunk_size)
        ]
        
        # Create learning phases
        for i, chunk in enumerate(chunks):
            phase = {
                "phase_number": i + 1,
                "objectives": chunk,
                "estimated_duration": sum(
                    learning_paths["estimated_duration"].get(obj, 30) for obj in chunk
                ),
                "difficulty_range": [
                    min(learning_paths["difficulty_progression"][primary_path.index(obj)] 
                        for obj in chunk if obj in primary_path),
                    max(learning_paths["difficulty_progression"][primary_path.index(obj)] 
                        for obj in chunk if obj in primary_path)
                ] if chunk else [1, 1]
            }
            
            optimized_sequence["learning_phases"].append(phase)
            optimized_sequence["phase_objectives"][f"phase_{i+1}"] = chunk
        
        optimized_sequence["total_phases"] = len(chunks)
        
        # Create milestones (every 2-3 phases)
        milestone_interval = max(2, len(chunks) // 3)
        for i in range(0, len(chunks), milestone_interval):
            milestone_phases = chunks[i:i + milestone_interval]
            milestone_objectives = [obj for phase in milestone_phases for obj in phase]
            
            optimized_sequence["milestones"].append({
                "milestone_number": len(optimized_sequence["milestones"]) + 1,
                "objectives_covered": milestone_objectives,
                "phase_range": [i + 1, min(i + milestone_interval, len(chunks))]
            })
        
        return optimized_sequence
    
    async def _create_hermit_guidance(
        self,
        user_query: str,
        optimized_sequence: Dict[str, Any],
        zpd_analysis: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Create wise guidance from The Hermit."""
        logger.debug("🏮 Creating hermit guidance...")
        
        sequence_summary = {
            "total_phases": optimized_sequence["total_phases"],
            "ready_to_learn": zpd_analysis["ready_to_learn"],
            "zpd_score": zpd_analysis["zpd_score"],
            "first_phase": optimized_sequence["learning_phases"][0] if optimized_sequence["learning_phases"] else None
        }
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As The Hermit 🏮, provide wise guidance for the seeker's learning journey:

Original Query: "{user_query}"

Learning Path Analysis:
- Total Learning Phases: {sequence_summary['total_phases']}
- Concepts Ready to Learn: {len(sequence_summary['ready_to_learn'])}
- ZPD Alignment Score: {sequence_summary['zpd_score']:.2f}
- First Phase Objectives: {sequence_summary['first_phase']['objectives'] if sequence_summary['first_phase'] else 'None'}

Provide your hermit wisdom including:
1. Encouragement for the journey ahead
2. Specific guidance for the first steps
3. Wisdom about the learning process
4. Warnings about common pitfalls
5. Your confidence in this path (0.0-1.0)

Speak with the patient wisdom of The Hermit, offering guidance that illuminates the path forward."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client, temperature=0.7)
        
        return {
            "hermit_wisdom": response,
            "reasoning": f"Path planned across {sequence_summary['total_phases']} phases with {sequence_summary['zpd_score']:.1%} ZPD alignment",
            "confidence": min(0.9, 0.6 + sequence_summary['zpd_score'] * 0.3)
        }
    
    def _compile_path_response(
        self,
        user_query: str,
        learning_objectives: List[str],
        optimized_sequence: Dict[str, Any],
        zpd_analysis: Dict[str, Any],
        hermit_guidance: Dict[str, Any]
    ) -> str:
        """Compile the final path planning response."""
        
        response = f"""🏮 **The Hermit's Learning Path**

**Seeker's Quest:** {user_query}

**Wisdom of the Path:**

{hermit_guidance["hermit_wisdom"]}

**Learning Journey Overview:**
• **Total Learning Phases:** {optimized_sequence['total_phases']}
• **Concepts in Zone of Proximal Development:** {len(zpd_analysis['ready_to_learn'])}
• **ZPD Alignment Score:** {zpd_analysis['zpd_score']:.1%}

**Your Learning Path:**"""
        
        # Add learning phases
        for phase in optimized_sequence["learning_phases"]:
            response += f"""

**Phase {phase['phase_number']}** (Est. {phase['estimated_duration']} min)
• Objectives: {', '.join(phase['objectives'])}
• Difficulty: {phase['difficulty_range'][0]}-{phase['difficulty_range'][1]}/10"""
        
        response += f"""

**Milestones:**"""
        
        for milestone in optimized_sequence["milestones"]:
            response += f"""
• **Milestone {milestone['milestone_number']}:** Complete Phases {milestone['phase_range'][0]}-{milestone['phase_range'][1]}"""
        
        response += f"""

**Sacred Guidance:**
• Start with Phase 1 objectives - they are within your Zone of Proximal Development
• Focus on understanding connections between concepts through [[bidirectional links]]
• Trust the process - each step builds upon the previous

*The path is illuminated. Let The Magician now weave the knowledge into understanding.*"""
        
        return response