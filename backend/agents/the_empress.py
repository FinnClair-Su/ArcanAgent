"""
The Empress Agent 🌸

Role: Memory Consolidation & Knowledge Integration
Wisdom: "Nurture growth through connection" - Transforms learning into lasting wisdom
Powers: Consolidates knowledge and creates integrated understanding

The Empress is the final agent in the learning pipeline, embodying the
nurturing aspect of knowledge consolidation. She takes the learning content
and assessment results, then weaves them into a coherent whole that can
be permanently integrated into the learner's knowledge base through
bidirectional links.
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict
from datetime import datetime, timedelta

from .base_agent import BaseAgent, AgentCapability, AgentResponse
from backend.core.context_manager import ContextManager, ContextPriority
from backend.core.tool_call_engine import ToolCallEngine, ToolCall
from backend.core.llm_client import BaseLLMClient, LLMMessage
from backend.core.bidirectional_links import BidirectionalLinkEngine

logger = logging.getLogger("ArcanAgent.TheEmpress")


class TheEmpress(BaseAgent):
    """
    The Empress Agent - Memory Consolidation & Knowledge Integration
    
    The Empress nurtures knowledge into wisdom through careful consolidation
    and integration. She transforms the learning session into lasting
    understanding that becomes part of the learner's permanent knowledge.
    """
    
    def __init__(
        self,
        link_engine: BidirectionalLinkEngine,
        context_manager: ContextManager,
        tool_engine: ToolCallEngine
    ):
        super().__init__(
            name="The Empress",
            tarot_card="🌸 The Empress",
            wisdom="Nurture growth through connection - Transforms learning into lasting wisdom",
            primary_capability=AgentCapability.MEMORY_CONSOLIDATION,
            link_engine=link_engine,
            context_manager=context_manager,
            tool_engine=tool_engine
        )
    
    def get_system_prompt(self) -> str:
        """Get The Empress's system prompt."""
        return """You are The Empress 🌸, the nurturing mother of wisdom and knowledge integration.

Your sacred role is to consolidate learning into lasting memory and integrate new knowledge seamlessly into the existing knowledge web. You possess the maternal wisdom to:

- Transform temporary learning into permanent understanding
- Create meaningful connections between new and existing knowledge
- Consolidate fragmented information into coherent mental models
- Nurture the growth of knowledge through careful integration
- Strengthen the bidirectional link network for better recall
- Create synthesis and higher-order understanding

Your consolidation follows these principles:
1. Honor what was learned while respecting existing knowledge
2. Create strong bidirectional links for lasting memory
3. Build coherent mental models from fragmented pieces
4. Synthesize insights that transcend individual concepts
5. Strengthen the knowledge network through strategic connections
6. Nurture understanding that grows and evolves over time

Speak with the nurturing wisdom of The Empress - be supportive, integrative, and help knowledge blossom into lasting wisdom. Your consolidation should make learning stick and grow.

Remember: True wisdom emerges when individual insights are woven together through bidirectional links into a living tapestry of understanding."""
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get The Empress's capabilities."""
        return [
            AgentCapability.MEMORY_CONSOLIDATION,
            AgentCapability.LINK_ANALYSIS,
            AgentCapability.COGNITIVE_ANALYSIS
        ]
    
    async def execute(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        llm_client: Optional[BaseLLMClient] = None
    ) -> AgentResponse:
        """Execute memory consolidation and knowledge integration."""
        logger.info(f"🌸 The Empress begins consolidation for: {user_query[:100]}...")
        
        try:
            # Get outputs from all previous agents
            priestess_assessment = context.get("high_priestess_assessment", {}) if context else {}
            hermit_plan = context.get("hermit_plan", {}) if context else {}
            magician_content = context.get("magician_content", {}) if context else {}
            justice_evaluation = context.get("justice_evaluation", {}) if context else {}
            
            # Step 1: Analyze the learning session
            session_analysis = await self._analyze_learning_session(
                user_query,
                priestess_assessment,
                hermit_plan,
                magician_content,
                justice_evaluation
            )
            
            # Step 2: Extract key insights and concepts
            key_insights = await self._extract_key_insights(
                session_analysis,
                magician_content,
                llm_client
            )
            
            # Step 3: Create consolidated memory structures
            memory_structures = await self._create_memory_structures(
                key_insights,
                session_analysis,
                llm_client
            )
            
            # Step 4: Integrate with existing knowledge base
            integration_results = await self._integrate_with_knowledge_base(
                memory_structures,
                key_insights
            )
            
            # Step 5: Strengthen bidirectional links
            link_strengthening = await self._strengthen_bidirectional_links(
                integration_results,
                memory_structures
            )
            
            # Step 6: Create consolidation wisdom
            consolidation_wisdom = await self._create_consolidation_wisdom(
                user_query,
                session_analysis,
                integration_results,
                llm_client
            )
            
            # Compile response
            response_content = self._compile_consolidation_response(
                user_query,
                session_analysis,
                memory_structures,
                integration_results,
                consolidation_wisdom
            )
            
            # Extract all links that were strengthened or created
            consolidated_links = self._extract_consolidated_links(
                memory_structures,
                integration_results
            )
            
            return AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=True,
                content=response_content,
                metadata={
                    "session_analysis": session_analysis,
                    "key_insights": key_insights,
                    "memory_structures": memory_structures,
                    "integration_results": integration_results,
                    "link_strengthening": link_strengthening,
                    "total_links_consolidated": len(consolidated_links)
                },
                reasoning=consolidation_wisdom.get("reasoning", ""),
                confidence=consolidation_wisdom.get("confidence", 0.9),
                links_discovered=consolidated_links
            )
            
        except Exception as e:
            logger.error(f"🌸 The Empress encountered an error: {e}")
            return AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=False,
                content=f"The nurturing energies are disturbed: {str(e)}",
                errors=[str(e)]
            )
    
    async def _analyze_learning_session(
        self,
        user_query: str,
        priestess_assessment: Dict[str, Any],
        hermit_plan: Dict[str, Any],
        magician_content: Dict[str, Any],
        justice_evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze the complete learning session."""
        logger.debug("🌸 Analyzing learning session...")
        
        session_analysis = {
            "learning_objectives_met": [],
            "knowledge_gaps_addressed": [],
            "new_connections_made": [],
            "comprehension_level": "developing",
            "session_quality": 0.0,
            "retention_factors": []
        }
        
        # Analyze what objectives were addressed
        initial_mastery = priestess_assessment.get("mastery_assessment", {}).get("overall_mastery", 0.0)
        final_comprehension = justice_evaluation.get("comprehension_score", {}).get("overall_score", 0.0)
        
        # Calculate learning progress
        learning_progress = max(0.0, final_comprehension - initial_mastery)
        
        # Extract content information
        generated_content = magician_content.get("generated_content", {})
        content_quality = len(generated_content.get("key_concepts", [])) / max(1, 10)  # Normalize
        
        # Identify objectives that were met
        hermit_objectives = hermit_plan.get("learning_objectives", [])
        comprehension_level = justice_evaluation.get("comprehension_score", {}).get("comprehension_level", "developing")
        
        if comprehension_level in ["good", "excellent"]:
            session_analysis["learning_objectives_met"] = hermit_objectives[:3]  # Top 3 objectives
        elif comprehension_level == "developing":
            session_analysis["learning_objectives_met"] = hermit_objectives[:2]  # Top 2 objectives
        else:
            session_analysis["learning_objectives_met"] = hermit_objectives[:1]  # Top 1 objective
        
        # Identify knowledge gaps that were addressed
        initial_gaps = priestess_assessment.get("mastery_assessment", {}).get("knowledge_gaps", [])
        session_analysis["knowledge_gaps_addressed"] = session_analysis["learning_objectives_met"]
        
        # Extract new connections from magician's work
        links_created = magician_content.get("metadata", {}).get("total_links_created", 0)
        session_analysis["new_connections_made"] = magician_content.get("linked_content", {}).get("links_added", [])
        
        # Determine overall session quality
        session_analysis["comprehension_level"] = comprehension_level
        session_analysis["session_quality"] = (
            learning_progress * 0.4 +
            content_quality * 0.3 +
            min(links_created / 10, 1.0) * 0.3
        )
        
        # Identify retention factors
        retention_factors = []
        if links_created > 5:
            retention_factors.append("rich_bidirectional_linking")
        if len(session_analysis["learning_objectives_met"]) > 2:
            retention_factors.append("multiple_concepts_mastered")
        if final_comprehension > 0.7:
            retention_factors.append("high_comprehension_achieved")
        
        session_analysis["retention_factors"] = retention_factors
        
        return session_analysis
    
    async def _extract_key_insights(
        self,
        session_analysis: Dict[str, Any],
        magician_content: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Extract key insights from the learning session."""
        logger.debug("🌸 Extracting key insights...")
        
        # Get content created by The Magician
        generated_content = magician_content.get("generated_content", {})
        content_text = generated_content.get("content", "")
        key_concepts = generated_content.get("key_concepts", [])
        
        # Get connection bridges
        bridges = magician_content.get("connection_bridges", {}).get("bridges", [])
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As The Empress 🌸, extract the key insights from this learning session:

Learning Content:
{content_text[:1500]}...

Key Concepts Covered: {', '.join(key_concepts)}
Learning Objectives Met: {', '.join(session_analysis['learning_objectives_met'])}
New Connections Made: {len(session_analysis['new_connections_made'])}
Session Quality: {session_analysis['session_quality']:.2f}

Extract the most important insights that should be consolidated into long-term memory:

1. **Core Insights**: The fundamental understanding gained
2. **Key Relationships**: Important connections between concepts
3. **Practical Applications**: How this knowledge can be used
4. **Integration Points**: How this connects to broader knowledge
5. **Memory Anchors**: Specific details that aid recall

Focus on insights that will have lasting value and can be built upon in future learning.

Return as a JSON object with these categories."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client)
        
        try:
            insights = json.loads(response)
            return {
                "core_insights": insights.get("core_insights", []),
                "key_relationships": insights.get("key_relationships", []),
                "practical_applications": insights.get("practical_applications", []),
                "integration_points": insights.get("integration_points", []),
                "memory_anchors": insights.get("memory_anchors", []),
                "extraction_quality": len(insights.get("core_insights", [])) / max(1, 5)
            }
        except json.JSONDecodeError:
            # Fallback extraction
            return {
                "core_insights": key_concepts[:3],
                "key_relationships": [f"{concept} connects to other learning areas" for concept in key_concepts[:2]],
                "practical_applications": ["Apply in real-world contexts"],
                "integration_points": session_analysis['learning_objectives_met'],
                "memory_anchors": key_concepts,
                "extraction_quality": 0.5
            }
    
    async def _create_memory_structures(
        self,
        key_insights: Dict[str, Any],
        session_analysis: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Create consolidated memory structures."""
        logger.debug("🌸 Creating memory structures...")
        
        # Organize insights into memory structures
        memory_structures = {
            "concept_clusters": {},
            "relationship_maps": {},
            "application_schemas": {},
            "integration_pathways": {},
            "retrieval_cues": {}
        }
        
        # Create concept clusters
        core_insights = key_insights.get("core_insights", [])
        for i, insight in enumerate(core_insights):
            cluster_id = f"cluster_{i+1}"
            memory_structures["concept_clusters"][cluster_id] = {
                "central_concept": insight,
                "supporting_concepts": key_insights.get("memory_anchors", [])[:3],
                "strength": session_analysis.get("session_quality", 0.5)
            }
        
        # Create relationship maps
        relationships = key_insights.get("key_relationships", [])
        for i, relationship in enumerate(relationships):
            map_id = f"relationship_{i+1}"
            memory_structures["relationship_maps"][map_id] = {
                "relationship": relationship,
                "strength": 0.8,  # Relationships from learning are initially strong
                "type": "learned_connection"
            }
        
        # Create application schemas
        applications = key_insights.get("practical_applications", [])
        for i, application in enumerate(applications):
            schema_id = f"application_{i+1}"
            memory_structures["application_schemas"][schema_id] = {
                "application": application,
                "context": "learning_session",
                "transferability": 0.7
            }
        
        # Create integration pathways
        integration_points = key_insights.get("integration_points", [])
        for i, point in enumerate(integration_points):
            pathway_id = f"pathway_{i+1}"
            memory_structures["integration_pathways"][pathway_id] = {
                "integration_point": point,
                "existing_knowledge": session_analysis.get("learning_objectives_met", []),
                "pathway_strength": 0.6
            }
        
        # Create retrieval cues
        memory_anchors = key_insights.get("memory_anchors", [])
        for i, anchor in enumerate(memory_anchors):
            cue_id = f"cue_{i+1}"
            memory_structures["retrieval_cues"][cue_id] = {
                "cue": anchor,
                "target_knowledge": core_insights,
                "cue_effectiveness": 0.8
            }
        
        return memory_structures
    
    async def _integrate_with_knowledge_base(
        self,
        memory_structures: Dict[str, Any],
        key_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Integrate new memory structures with existing knowledge base."""
        logger.debug("🌸 Integrating with knowledge base...")
        
        integration_results = {
            "new_notes_created": [],
            "existing_notes_updated": [],
            "new_links_created": [],
            "link_strengths_updated": {},
            "integration_score": 0.0
        }
        
        # Extract concepts that should become notes
        core_insights = key_insights.get("core_insights", [])
        memory_anchors = key_insights.get("memory_anchors", [])
        
        # Find existing notes that relate to new concepts
        all_concepts = core_insights + memory_anchors
        related_notes = {}
        
        for concept in all_concepts:
            concept_lower = concept.lower()
            
            # Search for existing notes
            for note_id, metadata in self.link_engine.note_metadata.items():
                title = metadata.get('title', '').lower()
                content = self.link_engine.note_content.get(note_id, '').lower()
                
                if concept_lower in title or concept_lower in content:
                    if concept not in related_notes:
                        related_notes[concept] = []
                    related_notes[concept].append(note_id)
        
        # Determine what needs to be created vs updated
        for concept in core_insights[:3]:  # Focus on top 3 insights
            if concept in related_notes:
                # Update existing notes
                integration_results["existing_notes_updated"].extend(related_notes[concept])
            else:
                # Create new note
                integration_results["new_notes_created"].append({
                    "title": concept,
                    "content_type": "consolidated_learning",
                    "source": "empress_consolidation"
                })
        
        # Create links between new and existing concepts
        relationship_maps = memory_structures.get("relationship_maps", {})
        for rel_id, rel_data in relationship_maps.items():
            relationship = rel_data["relationship"]
            
            # Extract concepts from relationship description
            concepts_in_relationship = [
                concept for concept in all_concepts 
                if concept.lower() in relationship.lower()
            ]
            
            # Create bidirectional links between related concepts
            for i, concept1 in enumerate(concepts_in_relationship):
                for concept2 in concepts_in_relationship[i+1:]:
                    link = f"{concept1} <-> {concept2}"
                    integration_results["new_links_created"].append(link)
                    integration_results["link_strengths_updated"][link] = rel_data["strength"]
        
        # Calculate integration score
        total_concepts = len(all_concepts)
        concepts_with_existing_notes = len([c for c in all_concepts if c in related_notes])
        new_links_created = len(integration_results["new_links_created"])
        
        integration_results["integration_score"] = (
            (concepts_with_existing_notes / max(1, total_concepts)) * 0.5 +
            min(new_links_created / 10, 1.0) * 0.5
        )
        
        return integration_results
    
    async def _strengthen_bidirectional_links(
        self,
        integration_results: Dict[str, Any],
        memory_structures: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Strengthen bidirectional links for better memory consolidation."""
        logger.debug("🌸 Strengthening bidirectional links...")
        
        strengthening_results = {
            "links_strengthened": [],
            "new_pathways_created": [],
            "network_density_improvement": 0.0,
            "consolidation_quality": 0.0
        }
        
        # Strengthen links identified in integration
        new_links = integration_results.get("new_links_created", [])
        link_strengths = integration_results.get("link_strengths_updated", {})
        
        for link in new_links:
            if link in link_strengths:
                strength = link_strengths[link]
                if strength > 0.6:  # Only strengthen high-quality links
                    strengthening_results["links_strengthened"].append({
                        "link": link,
                        "strength": strength,
                        "strengthening_factor": min(1.0, strength + 0.2)
                    })
        
        # Create pathways between concept clusters
        concept_clusters = memory_structures.get("concept_clusters", {})
        cluster_ids = list(concept_clusters.keys())
        
        for i, cluster1_id in enumerate(cluster_ids):
            for cluster2_id in cluster_ids[i+1:]:
                cluster1 = concept_clusters[cluster1_id]
                cluster2 = concept_clusters[cluster2_id]
                
                # Create pathway if clusters have sufficient strength
                if (cluster1["strength"] > 0.5 and cluster2["strength"] > 0.5):
                    pathway = {
                        "from_cluster": cluster1["central_concept"],
                        "to_cluster": cluster2["central_concept"],
                        "pathway_strength": (cluster1["strength"] + cluster2["strength"]) / 2
                    }
                    strengthening_results["new_pathways_created"].append(pathway)
        
        # Calculate network improvements
        total_links_affected = len(strengthening_results["links_strengthened"])
        pathways_created = len(strengthening_results["new_pathways_created"])
        
        strengthening_results["network_density_improvement"] = (
            min(total_links_affected / 10, 1.0) * 0.6 +
            min(pathways_created / 5, 1.0) * 0.4
        )
        
        strengthening_results["consolidation_quality"] = min(1.0, 
            strengthening_results["network_density_improvement"] * 1.2
        )
        
        return strengthening_results
    
    async def _create_consolidation_wisdom(
        self,
        user_query: str,
        session_analysis: Dict[str, Any],
        integration_results: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Create wisdom about the consolidation process."""
        logger.debug("🌸 Creating consolidation wisdom...")
        
        consolidation_summary = {
            "objectives_met": len(session_analysis["learning_objectives_met"]),
            "session_quality": session_analysis["session_quality"],
            "integration_score": integration_results["integration_score"],
            "new_notes": len(integration_results["new_notes_created"]),
            "new_links": len(integration_results["new_links_created"])
        }
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As The Empress 🌸, provide nurturing wisdom about this learning consolidation:

Original Learning Request: "{user_query}"

Consolidation Results:
- Learning Objectives Met: {consolidation_summary['objectives_met']}
- Session Quality: {consolidation_summary['session_quality']:.2f}
- Knowledge Integration Score: {consolidation_summary['integration_score']:.2f}
- New Knowledge Structures Created: {consolidation_summary['new_notes']}
- New Bidirectional Links Formed: {consolidation_summary['new_links']}

Provide your nurturing wisdom including:
1. Recognition of the growth that has occurred
2. How this learning will serve them in the future
3. Guidance for continued knowledge development
4. Encouragement for the learning journey
5. Your confidence in this consolidation (0.0-1.0)

Speak with the loving wisdom of The Empress, celebrating growth while nurturing future potential."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client, temperature=0.8)
        
        return {
            "consolidation_wisdom": response,
            "reasoning": f"Consolidated {consolidation_summary['objectives_met']} objectives with {consolidation_summary['integration_score']:.1%} integration success",
            "confidence": min(0.95, 0.8 + consolidation_summary['integration_score'] * 0.15)
        }
    
    def _extract_consolidated_links(
        self,
        memory_structures: Dict[str, Any],
        integration_results: Dict[str, Any]
    ) -> Set[str]:
        """Extract all links that were consolidated."""
        consolidated_links = set()
        
        # Add links from memory structures
        relationship_maps = memory_structures.get("relationship_maps", {})
        for rel_data in relationship_maps.values():
            relationship = rel_data["relationship"]
            # Extract potential links from relationship descriptions
            words = relationship.split()
            for word in words:
                if len(word) > 3 and word.isalpha():
                    consolidated_links.add(word.lower())
        
        # Add links from integration results
        new_links = integration_results.get("new_links_created", [])
        for link in new_links:
            # Extract concepts from bidirectional link notation
            if " <-> " in link:
                concepts = link.split(" <-> ")
                consolidated_links.update(concepts)
        
        return consolidated_links
    
    def _compile_consolidation_response(
        self,
        user_query: str,
        session_analysis: Dict[str, Any],
        memory_structures: Dict[str, Any],
        integration_results: Dict[str, Any],
        consolidation_wisdom: Dict[str, Any]
    ) -> str:
        """Compile the final consolidation response."""
        
        response = f"""🌸 **The Empress's Knowledge Consolidation**

**Learning Journey:** {user_query}

**Nurturing Wisdom:**

{consolidation_wisdom['consolidation_wisdom']}

**Consolidation Results:**
• **Learning Objectives Achieved:** {len(session_analysis['learning_objectives_met'])}
• **Session Quality:** {session_analysis['session_quality']:.1%}
• **Knowledge Integration Score:** {integration_results['integration_score']:.1%}
• **Comprehension Level:** {session_analysis['comprehension_level'].replace('_', ' ').title()}

**Memory Consolidation:**
• **New Knowledge Structures:** {len(integration_results['new_notes_created'])}
• **Existing Knowledge Enhanced:** {len(integration_results['existing_notes_updated'])}
• **New Bidirectional Links:** {len(integration_results['new_links_created'])}
• **Connection Strength:** Enhanced through strategic linking

**Knowledge Integration:**
• **Memory Anchors Created:** {len(memory_structures.get('retrieval_cues', {}))}
• **Concept Clusters Formed:** {len(memory_structures.get('concept_clusters', {}))}
• **Application Pathways:** {len(memory_structures.get('application_schemas', {}))}

**Growth Achieved:**"""
        
        # Add specific achievements
        objectives_met = session_analysis.get('learning_objectives_met', [])
        for objective in objectives_met[:3]:
            response += f"\n• Mastered: [[{objective}]]"
        
        response += f"""

**Retention Factors:**"""
        
        retention_factors = session_analysis.get('retention_factors', [])
        factor_descriptions = {
            'rich_bidirectional_linking': 'Strong [[bidirectional links]] enhance memory recall',
            'multiple_concepts_mastered': 'Multiple interconnected concepts reinforce each other',
            'high_comprehension_achieved': 'Deep understanding creates lasting knowledge'
        }
        
        for factor in retention_factors:
            description = factor_descriptions.get(factor, f'{factor.replace("_", " ").title()} enhances retention')
            response += f"\n• {description}"
        
        response += f"""

**Sacred Integration:**
Your learning has been woven into the tapestry of knowledge through {len(integration_results['new_links_created'])} new bidirectional links. These connections ensure that what you've learned today will flourish and grow, connecting to future insights and deepening your understanding over time.

**Empress's Blessing:**
The seeds of knowledge have been planted and nurtured. As you continue your learning journey, these concepts will bloom into greater wisdom, each [[bidirectional link]] a pathway to deeper understanding.

*Your knowledge has been consolidated with love. The learning cycle is complete, but your growth continues forever.*"""
        
        return response