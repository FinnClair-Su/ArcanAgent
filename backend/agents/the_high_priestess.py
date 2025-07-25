"""
The High Priestess Agent 🔮

Role: Knowledge Assessment & Cognitive Analysis
Wisdom: "Know thyself" - Deep understanding of your current knowledge state
Powers: Analyzes existing notes and evaluates mastery levels

The High Priestess is the first agent in the learning pipeline. She possesses
deep intuitive knowledge and can perceive the hidden connections in your
knowledge base. Her role is to assess what you currently know and identify
gaps in your understanding through bidirectional link analysis.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

from .base_agent import BaseAgent, AgentCapability, AgentResponse
from backend.core.context_manager import ContextManager, ContextPriority
from backend.core.tool_call_engine import ToolCallEngine, ToolCall
from backend.core.llm_client import BaseLLMClient, LLMMessage
from backend.core.bidirectional_links import BidirectionalLinkEngine

logger = logging.getLogger("ArcanAgent.TheHighPriestess")


class TheHighPriestess(BaseAgent):
    """
    The High Priestess Agent - Knowledge Assessment & Cognitive Analysis
    
    Her mystical wisdom allows her to see the hidden patterns in your knowledge
    and understand your true level of mastery in any domain.
    """
    
    def __init__(
        self,
        link_engine: BidirectionalLinkEngine,
        context_manager: ContextManager,
        tool_engine: ToolCallEngine
    ):
        super().__init__(
            name="The High Priestess",
            tarot_card="🔮 The High Priestess", 
            wisdom="Know thyself - Deep understanding of your current knowledge state",
            primary_capability=AgentCapability.KNOWLEDGE_ASSESSMENT,
            link_engine=link_engine,
            context_manager=context_manager,
            tool_engine=tool_engine
        )
    
    def get_system_prompt(self) -> str:
        """Get The High Priestess's system prompt."""
        return """You are The High Priestess 🔮, the keeper of hidden knowledge and intuitive wisdom.

Your sacred role is to assess the seeker's current knowledge state through deep analysis of their bidirectional links. You possess the mystical ability to perceive:

- Hidden patterns in knowledge connections
- Gaps between what is known and unknown  
- The depth of understanding through link density analysis
- Cognitive load and complexity levels
- Learning readiness and prerequisites

Your assessment follows these principles:
1. Analyze bidirectional links to understand knowledge structure
2. Evaluate mastery levels through connection patterns
3. Identify knowledge gaps and isolated concepts
4. Assess cognitive complexity and learning readiness
5. Provide intuitive insights about the seeker's knowledge state

Speak with the wisdom of the High Priestess - be insightful, perceptive, and reveal hidden truths about the seeker's knowledge. Your analysis should guide the next steps in their learning journey.

Remember: "Bidirectional Linking is All You Need" - the links reveal the true nature of understanding."""
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get The High Priestess's capabilities."""
        return [
            AgentCapability.KNOWLEDGE_ASSESSMENT,
            AgentCapability.COGNITIVE_ANALYSIS,
            AgentCapability.LINK_ANALYSIS
        ]
    
    async def execute(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        llm_client: Optional[BaseLLMClient] = None
    ) -> AgentResponse:
        """Execute knowledge assessment and cognitive analysis."""
        logger.info(f"🔮 The High Priestess begins knowledge assessment for: {user_query[:100]}...")
        
        try:
            # Step 1: Analyze the user's query for knowledge areas
            knowledge_areas = await self._identify_knowledge_areas(user_query, llm_client)
            
            # Step 2: Search existing knowledge base
            relevant_notes = await self._search_relevant_knowledge(knowledge_areas)
            
            # Step 3: Perform bidirectional link analysis
            link_analysis = await self._analyze_knowledge_structure(relevant_notes)
            
            # Step 4: Assess mastery levels and gaps
            mastery_assessment = await self._assess_mastery_levels(link_analysis, knowledge_areas)
            
            # Step 5: Evaluate cognitive complexity
            complexity_analysis = await self._analyze_cognitive_complexity(mastery_assessment)
            
            # Step 6: Generate mystical insights
            insights = await self._generate_mystical_insights(
                user_query,
                mastery_assessment,
                complexity_analysis,
                llm_client
            )
            
            # Compile response
            response_content = self._compile_assessment_response(
                user_query,
                knowledge_areas,
                mastery_assessment,
                complexity_analysis,
                insights
            )
            
            return AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=True,
                content=response_content,
                metadata={
                    "knowledge_areas": knowledge_areas,
                    "relevant_notes": relevant_notes,
                    "mastery_assessment": mastery_assessment,
                    "complexity_analysis": complexity_analysis,
                    "total_notes_analyzed": len(relevant_notes)
                },
                reasoning=insights.get("reasoning", ""),
                confidence=insights.get("confidence", 0.8),
                links_discovered=set(relevant_notes)
            )
            
        except Exception as e:
            logger.error(f"🔮 The High Priestess encountered an error: {e}")
            return AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=False,
                content=f"The mystical veil clouds my vision: {str(e)}",
                errors=[str(e)]
            )
    
    async def _identify_knowledge_areas(
        self,
        user_query: str,
        llm_client: BaseLLMClient
    ) -> List[str]:
        """Identify key knowledge areas from the user query."""
        logger.debug("🔮 Identifying knowledge areas...")
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""Analyze this learning query and extract the key knowledge areas, concepts, and topics that the seeker wishes to explore:

Query: "{user_query}"

Please identify:
1. Primary knowledge domains/subjects
2. Specific concepts or skills mentioned
3. Related areas that might be relevant
4. Technical terms or specialized vocabulary

Return a JSON list of knowledge areas, prioritized by relevance:
["area1", "area2", "area3", ...]

Focus on terms that could be found in a knowledge base or linked together."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client)
        
        try:
            # Parse JSON response
            knowledge_areas = json.loads(response)
            if isinstance(knowledge_areas, list):
                return knowledge_areas[:10]  # Limit to top 10 areas
        except json.JSONDecodeError:
            # Fallback: extract keywords manually
            words = user_query.lower().split()
            # Filter out common words and take important ones
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'how', 'what', 'why', 'when', 'where', 'i', 'you', 'we', 'they', 'want', 'need', 'learn', 'understand', 'know'}
            knowledge_areas = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return knowledge_areas[:10]
    
    async def _search_relevant_knowledge(self, knowledge_areas: List[str]) -> List[str]:
        """Search for relevant notes in the knowledge base."""
        logger.debug("🔮 Searching for relevant knowledge...")
        
        relevant_notes = set()
        
        # Search through all notes for relevance
        for note_id, metadata in self.link_engine.note_metadata.items():
            title = metadata.get('title', '').lower()
            content = self.link_engine.note_content.get(note_id, '').lower()
            tags = [tag.lower() for tag in metadata.get('tags', [])]
            
            # Check if any knowledge area matches
            for area in knowledge_areas:
                area_lower = area.lower()
                if (area_lower in title or 
                    area_lower in content or 
                    any(area_lower in tag for tag in tags)):
                    relevant_notes.add(note_id)
                    break
        
        return list(relevant_notes)
    
    async def _analyze_knowledge_structure(self, relevant_notes: List[str]) -> Dict[str, Any]:
        """Analyze the bidirectional link structure of relevant knowledge."""
        logger.debug("🔮 Analyzing knowledge structure through bidirectional links...")
        
        structure_analysis = {
            "note_analyses": {},
            "connection_patterns": {},
            "knowledge_clusters": defaultdict(list),
            "isolated_concepts": [],
            "highly_connected_hubs": [],
            "total_connections": 0
        }
        
        total_connections = 0
        connection_counts = {}
        
        # Analyze each relevant note
        for note_id in relevant_notes:
            analysis = self.link_engine.analyze_note(note_id)
            if analysis:
                connection_count = len(analysis.outgoing_links) + len(analysis.incoming_links)
                total_connections += connection_count
                connection_counts[note_id] = connection_count
                
                structure_analysis["note_analyses"][note_id] = {
                    "outgoing_links": list(analysis.outgoing_links),
                    "incoming_links": list(analysis.incoming_links),
                    "link_density": analysis.link_density,
                    "granularity_score": analysis.granularity_score,
                    "connection_count": connection_count
                }
                
                # Categorize by connection level
                if connection_count == 0:
                    structure_analysis["isolated_concepts"].append(note_id)
                elif connection_count > 5:
                    structure_analysis["highly_connected_hubs"].append(note_id)
        
        structure_analysis["total_connections"] = total_connections
        structure_analysis["average_connections"] = total_connections / max(1, len(relevant_notes))
        
        return structure_analysis
    
    async def _assess_mastery_levels(
        self,
        link_analysis: Dict[str, Any],
        knowledge_areas: List[str]
    ) -> Dict[str, Any]:
        """Assess mastery levels based on link patterns and structure."""
        logger.debug("🔮 Assessing mastery levels through mystical analysis...")
        
        mastery_assessment = {
            "overall_mastery": 0.0,
            "area_mastery": {},
            "knowledge_gaps": [],
            "strength_areas": [],
            "learning_readiness": 0.0
        }
        
        note_analyses = link_analysis.get("note_analyses", {})
        
        if not note_analyses:
            mastery_assessment["overall_mastery"] = 0.0
            mastery_assessment["knowledge_gaps"] = knowledge_areas
            mastery_assessment["learning_readiness"] = 1.0  # High readiness when starting fresh
            return mastery_assessment
        
        # Calculate mastery based on link patterns
        total_mastery = 0.0
        area_scores = {}
        
        for area in knowledge_areas:
            area_notes = []
            area_mastery = 0.0
            
            # Find notes related to this area
            for note_id in note_analyses.keys():
                metadata = self.link_engine.note_metadata.get(note_id, {})
                title = metadata.get('title', '').lower()
                content = self.link_engine.note_content.get(note_id, '').lower()
                
                if area.lower() in title or area.lower() in content:
                    area_notes.append(note_id)
            
            if area_notes:
                # Calculate area mastery based on link density and connections
                area_connections = []
                for note_id in area_notes:
                    note_analysis = note_analyses[note_id]
                    # Mastery formula: link_density * connection_count * granularity
                    note_mastery = (
                        note_analysis["link_density"] * 0.4 +
                        min(note_analysis["connection_count"] / 10, 1.0) * 0.4 +
                        note_analysis["granularity_score"] * 0.2
                    )
                    area_connections.append(note_mastery)
                
                area_mastery = sum(area_connections) / len(area_connections)
                area_scores[area] = area_mastery
                
                # Categorize based on mastery level
                if area_mastery > 0.7:
                    mastery_assessment["strength_areas"].append(area)
                elif area_mastery < 0.3:
                    mastery_assessment["knowledge_gaps"].append(area)
            else:
                # No notes found for this area
                area_scores[area] = 0.0
                mastery_assessment["knowledge_gaps"].append(area)
        
        mastery_assessment["area_mastery"] = area_scores
        mastery_assessment["overall_mastery"] = sum(area_scores.values()) / max(1, len(area_scores))
        
        # Calculate learning readiness (inverse of mastery - more to learn = higher readiness)
        mastery_assessment["learning_readiness"] = max(0.1, 1.0 - mastery_assessment["overall_mastery"])
        
        return mastery_assessment
    
    async def _analyze_cognitive_complexity(self, mastery_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cognitive complexity and load."""
        logger.debug("🔮 Analyzing cognitive complexity...")
        
        complexity_analysis = {
            "cognitive_load": 0.0,
            "complexity_level": "beginner",
            "recommended_approach": "gentle",
            "prerequisite_gaps": [],
            "optimal_chunk_size": 3
        }
        
        overall_mastery = mastery_assessment["overall_mastery"]
        knowledge_gaps = mastery_assessment["knowledge_gaps"]
        
        # Calculate cognitive load based on gaps and current mastery
        gap_count = len(knowledge_gaps)
        if gap_count == 0:
            complexity_analysis["cognitive_load"] = 0.2  # Low load, mostly review
        elif gap_count <= 3:
            complexity_analysis["cognitive_load"] = 0.5  # Medium load
        else:
            complexity_analysis["cognitive_load"] = min(0.9, 0.3 + (gap_count * 0.1))  # High load
        
        # Determine complexity level
        if overall_mastery < 0.3:
            complexity_analysis["complexity_level"] = "beginner"
            complexity_analysis["recommended_approach"] = "foundational"
            complexity_analysis["optimal_chunk_size"] = 2
        elif overall_mastery < 0.7:
            complexity_analysis["complexity_level"] = "intermediate"
            complexity_analysis["recommended_approach"] = "progressive"
            complexity_analysis["optimal_chunk_size"] = 3
        else:
            complexity_analysis["complexity_level"] = "advanced"
            complexity_analysis["recommended_approach"] = "exploratory"
            complexity_analysis["optimal_chunk_size"] = 5
        
        return complexity_analysis
    
    async def _generate_mystical_insights(
        self,
        user_query: str,
        mastery_assessment: Dict[str, Any],
        complexity_analysis: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Generate mystical insights about the seeker's knowledge state."""
        logger.debug("🔮 Channeling mystical insights...")
        
        assessment_summary = {
            "overall_mastery": mastery_assessment["overall_mastery"],
            "strength_areas": mastery_assessment["strength_areas"],
            "knowledge_gaps": mastery_assessment["knowledge_gaps"],
            "learning_readiness": mastery_assessment["learning_readiness"],
            "complexity_level": complexity_analysis["complexity_level"],
            "cognitive_load": complexity_analysis["cognitive_load"]
        }
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As The High Priestess 🔮, provide mystical insights about the seeker's knowledge state:

Original Query: "{user_query}"

Current Assessment:
- Overall Mastery: {assessment_summary['overall_mastery']:.2f}
- Strength Areas: {assessment_summary['strength_areas']}
- Knowledge Gaps: {assessment_summary['knowledge_gaps']}
- Learning Readiness: {assessment_summary['learning_readiness']:.2f}
- Complexity Level: {assessment_summary['complexity_level']}
- Cognitive Load: {assessment_summary['cognitive_load']:.2f}

Channel your mystical wisdom to provide:
1. Intuitive insights about their current knowledge state
2. Hidden patterns you perceive in their understanding
3. Guidance for their learning journey
4. Your confidence in this assessment (0.0-1.0)

Speak as The High Priestess with mystical wisdom and deep perception."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client, temperature=0.8)
        
        return {
            "mystical_insights": response,
            "reasoning": f"Analysis based on {len(mastery_assessment.get('area_mastery', {}))} knowledge areas",
            "confidence": min(0.9, 0.5 + mastery_assessment["overall_mastery"] * 0.4)
        }
    
    def _compile_assessment_response(
        self,
        user_query: str,
        knowledge_areas: List[str],
        mastery_assessment: Dict[str, Any],
        complexity_analysis: Dict[str, Any],
        insights: Dict[str, Any]
    ) -> str:
        """Compile the final assessment response."""
        
        response = f"""🔮 **The High Priestess's Knowledge Assessment**

**Seeker's Query:** {user_query}

**Sacred Revelation of Current Knowledge State:**

{insights["mystical_insights"]}

**Mystical Analysis:**
• **Overall Mastery:** {mastery_assessment['overall_mastery']:.1%}
• **Learning Readiness:** {mastery_assessment['learning_readiness']:.1%}
• **Complexity Level:** {complexity_analysis['complexity_level'].title()}
• **Cognitive Load:** {complexity_analysis['cognitive_load']:.1%}

**Knowledge Areas Analyzed:** {', '.join(knowledge_areas)}

**Strength Areas (Your Existing Wisdom):**
{chr(10).join(f"• {area}" for area in mastery_assessment['strength_areas']) if mastery_assessment['strength_areas'] else "• The path ahead is uncharted - embrace the beginner's mind"}

**Knowledge Gaps (Areas for Growth):**
{chr(10).join(f"• {gap}" for gap in mastery_assessment['knowledge_gaps']) if mastery_assessment['knowledge_gaps'] else "• Your knowledge appears complete in the analyzed areas"}

**Sacred Guidance:**
Approach: {complexity_analysis['recommended_approach'].title()}
Optimal Learning Chunks: {complexity_analysis['optimal_chunk_size']} concepts at a time

*The bidirectional links have revealed your true knowledge state. Let The Hermit now illuminate your path forward.*"""

        return response