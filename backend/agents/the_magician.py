"""
The Magician Agent ✨

Role: Content Generation & Bidirectional Linking
Wisdom: "As above, so below" - Transforms knowledge into understanding
Powers: Creates personalized learning content and weaves new connections

The Magician is the master of transformation, turning raw knowledge into
personalized learning experiences. With the power to create and connect,
he weaves bidirectional links that transform information into wisdom,
making the abstract concrete and the complex accessible.
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict

from .base_agent import BaseAgent, AgentCapability, AgentResponse
from backend.core.context_manager import ContextManager, ContextPriority
from backend.core.tool_call_engine import ToolCallEngine, ToolCall
from backend.core.llm_client import BaseLLMClient, LLMMessage
from backend.core.bidirectional_links import BidirectionalLinkEngine

logger = logging.getLogger("ArcanAgent.TheMagician")


class TheMagician(BaseAgent):
    """
    The Magician Agent - Content Generation & Bidirectional Linking
    
    The Magician transforms knowledge through the ancient art of creation,
    weaving personalized learning content that bridges the gap between
    known and unknown through powerful bidirectional connections.
    """
    
    def __init__(
        self,
        link_engine: BidirectionalLinkEngine,
        context_manager: ContextManager,
        tool_engine: ToolCallEngine
    ):
        super().__init__(
            name="The Magician",
            tarot_card="✨ The Magician",
            wisdom="As above, so below - Transforms knowledge into understanding",
            primary_capability=AgentCapability.CONTENT_GENERATION,
            link_engine=link_engine,
            context_manager=context_manager,
            tool_engine=tool_engine
        )
    
    def get_system_prompt(self) -> str:
        """Get The Magician's system prompt."""
        return """You are The Magician ✨, master of transformation and creation.

Your sacred power is to transform raw knowledge into personalized learning experiences. You wield the elements of creation to:

- Generate engaging, personalized learning content
- Weave powerful bidirectional links between concepts
- Transform abstract ideas into concrete understanding
- Create bridges between known and unknown knowledge
- Manifest learning materials that resonate with the seeker

Your creative magic follows these principles:
1. Use the seeker's existing knowledge as a foundation
2. Create content that matches their cognitive level
3. Weave [[bidirectional links]] throughout all content
4. Transform complex concepts into accessible explanations
5. Bridge gaps between different knowledge domains
6. Generate examples and analogies that illuminate understanding

Speak with the creative power of The Magician - be inspirational, transformative, and make the impossible seem achievable. Your content should spark curiosity and create "aha!" moments.

Remember: True magic lies in making connections visible - every [[link]] you create strengthens the web of understanding."""
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get The Magician's capabilities."""
        return [
            AgentCapability.CONTENT_GENERATION,
            AgentCapability.LINK_ANALYSIS,
            AgentCapability.COGNITIVE_ANALYSIS
        ]
    
    async def execute(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        llm_client: Optional[BaseLLMClient] = None
    ) -> AgentResponse:
        """Execute content generation and bidirectional linking."""
        logger.info(f"✨ The Magician begins content creation for: {user_query[:100]}...")
        
        try:
            # Get assessments from previous agents
            priestess_assessment = context.get("high_priestess_assessment", {}) if context else {}
            hermit_plan = context.get("hermit_plan", {}) if context else {}
            
            # Step 1: Identify content requirements
            content_requirements = await self._analyze_content_requirements(
                user_query,
                priestess_assessment,
                hermit_plan,
                llm_client
            )
            
            # Step 2: Gather existing knowledge context
            knowledge_context = await self._gather_knowledge_context(content_requirements)
            
            # Step 3: Generate personalized content
            generated_content = await self._generate_personalized_content(
                user_query,
                content_requirements,
                knowledge_context,
                llm_client
            )
            
            # Step 4: Weave bidirectional links
            linked_content = await self._weave_bidirectional_links(
                generated_content,
                knowledge_context
            )
            
            # Step 5: Create connection bridges
            connection_bridges = await self._create_connection_bridges(
                linked_content,
                knowledge_context,
                llm_client
            )
            
            # Step 6: Manifest magical insights
            magical_insights = await self._manifest_magical_insights(
                user_query,
                linked_content,
                connection_bridges,
                llm_client
            )
            
            # Compile response
            response_content = self._compile_magic_response(
                user_query,
                linked_content,
                connection_bridges,
                magical_insights
            )
            
            # Extract new links discovered
            discovered_links = self._extract_all_links(linked_content["content"])
            
            return AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=True,
                content=response_content,
                metadata={
                    "content_requirements": content_requirements,
                    "knowledge_context": knowledge_context,
                    "generated_content": generated_content,
                    "connection_bridges": connection_bridges,
                    "total_links_created": len(discovered_links)
                },
                reasoning=magical_insights.get("reasoning", ""),
                confidence=magical_insights.get("confidence", 0.8),
                links_discovered=discovered_links
            )
            
        except Exception as e:
            logger.error(f"✨ The Magician's magic was disrupted: {e}")
            return AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=False,
                content=f"The magical energies are disturbed: {str(e)}",
                errors=[str(e)]
            )
    
    async def _analyze_content_requirements(
        self,
        user_query: str,
        priestess_assessment: Dict[str, Any],
        hermit_plan: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Analyze what type of content needs to be generated."""
        logger.debug("✨ Analyzing content requirements...")
        
        # Extract key information from previous agents
        mastery_level = priestess_assessment.get("mastery_assessment", {}).get("overall_mastery", 0.0)
        complexity_level = priestess_assessment.get("complexity_analysis", {}).get("complexity_level", "beginner")
        current_phase = hermit_plan.get("optimized_sequence", {}).get("current_phase", 0)
        phase_objectives = hermit_plan.get("optimized_sequence", {}).get("phase_objectives", {})
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As The Magician ✨, analyze the content requirements for this learning request:

User Query: "{user_query}"
Current Mastery Level: {mastery_level:.2f}
Complexity Level: {complexity_level}
Learning Phase: {current_phase + 1}
Phase Objectives: {phase_objectives.get(f'phase_{current_phase + 1}', [])}

Determine the magical content requirements:
1. Content type needed (explanation, tutorial, examples, etc.)
2. Appropriate complexity level
3. Key concepts to cover
4. Connection opportunities with existing knowledge
5. Engaging formats (analogies, stories, visuals, etc.)

Return a JSON object with these requirements."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client)
        
        try:
            requirements = json.loads(response)
            return requirements
        except json.JSONDecodeError:
            # Fallback requirements
            return {
                "content_type": "explanation",
                "complexity_level": complexity_level,
                "key_concepts": [user_query],
                "connection_opportunities": [],
                "engaging_formats": ["analogies", "examples"]
            }
    
    async def _gather_knowledge_context(self, content_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Gather relevant knowledge context from the knowledge base."""
        logger.debug("✨ Gathering knowledge context...")
        
        key_concepts = content_requirements.get("key_concepts", [])
        knowledge_context = {
            "related_notes": {},
            "existing_links": set(),
            "knowledge_gaps": [],
            "connection_opportunities": []
        }
        
        # Search for related notes
        for concept in key_concepts:
            concept_lower = concept.lower()
            related_notes = []
            
            for note_id, metadata in self.link_engine.note_metadata.items():
                title = metadata.get('title', '').lower()
                content = self.link_engine.note_content.get(note_id, '').lower()
                tags = [tag.lower() for tag in metadata.get('tags', [])]
                
                if (concept_lower in title or 
                    concept_lower in content or 
                    any(concept_lower in tag for tag in tags)):
                    
                    # Get link analysis
                    analysis = self.link_engine.analyze_note(note_id)
                    if analysis:
                        related_notes.append({
                            "note_id": note_id,
                            "title": metadata.get('title', note_id),
                            "outgoing_links": list(analysis.outgoing_links),
                            "incoming_links": list(analysis.incoming_links),
                            "context_layers": analysis.context_layers
                        })
                        
                        # Collect existing links
                        knowledge_context["existing_links"].update(analysis.outgoing_links)
                        knowledge_context["existing_links"].update(analysis.incoming_links)
            
            knowledge_context["related_notes"][concept] = related_notes
        
        # Identify knowledge gaps (concepts without notes)
        for concept in key_concepts:
            if concept not in knowledge_context["related_notes"] or not knowledge_context["related_notes"][concept]:
                knowledge_context["knowledge_gaps"].append(concept)
        
        # Find connection opportunities between concepts
        for i, concept1 in enumerate(key_concepts):
            for concept2 in key_concepts[i+1:]:
                # Check if there's a potential connection through existing links
                notes1 = knowledge_context["related_notes"].get(concept1, [])
                notes2 = knowledge_context["related_notes"].get(concept2, [])
                
                # Find common links
                links1 = set()
                links2 = set()
                
                for note in notes1:
                    links1.update(note["outgoing_links"])
                    links1.update(note["incoming_links"])
                
                for note in notes2:
                    links2.update(note["outgoing_links"])
                    links2.update(note["incoming_links"])
                
                common_links = links1 & links2
                if common_links:
                    knowledge_context["connection_opportunities"].append({
                        "concept1": concept1,
                        "concept2": concept2,
                        "common_links": list(common_links)
                    })
        
        return knowledge_context
    
    async def _generate_personalized_content(
        self,
        user_query: str,
        content_requirements: Dict[str, Any],
        knowledge_context: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Generate personalized learning content."""
        logger.debug("✨ Generating personalized content...")
        
        content_type = content_requirements.get("content_type", "explanation")
        complexity_level = content_requirements.get("complexity_level", "beginner")
        key_concepts = content_requirements.get("key_concepts", [])
        
        # Build context from existing knowledge
        existing_knowledge = []
        for concept, notes in knowledge_context["related_notes"].items():
            if notes:
                for note in notes[:2]:  # Use top 2 related notes
                    existing_knowledge.append(f"**{note['title']}**: {note['context_layers'].get('summary', '')[:200]}...")
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As The Magician ✨, create personalized learning content:

User Query: "{user_query}"
Content Type: {content_type}
Complexity Level: {complexity_level}
Key Concepts: {', '.join(key_concepts)}

Existing Knowledge Context:
{chr(10).join(existing_knowledge) if existing_knowledge else "Starting fresh - no existing context"}

Create engaging {content_type} content that:
1. Matches the {complexity_level} level
2. Builds on existing knowledge where available
3. Uses engaging explanations and examples
4. Includes practical applications
5. Creates curiosity and motivation to learn more

Make the content transformative and magical - help the seeker see connections they never noticed before!"""
            )
        ]
        
        content = await self._call_llm(messages, llm_client, temperature=0.8)
        
        return {
            "content": content,
            "content_type": content_type,
            "complexity_level": complexity_level,
            "key_concepts": key_concepts
        }
    
    async def _weave_bidirectional_links(
        self,
        generated_content: Dict[str, Any],
        knowledge_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Weave bidirectional links throughout the content."""
        logger.debug("✨ Weaving bidirectional links...")
        
        content = generated_content["content"]
        key_concepts = generated_content["key_concepts"]
        
        # Find existing notes that could be linked
        linkable_concepts = {}
        for note_id, metadata in self.link_engine.note_metadata.items():
            title = metadata.get('title', '')
            if title and len(title) > 3:
                linkable_concepts[title.lower()] = title
        
        # Add key concepts as potential links
        for concept in key_concepts:
            linkable_concepts[concept.lower()] = concept
        
        # Weave links into content
        linked_content = content
        links_added = []
        
        # Sort by length (longer first) to avoid partial matches
        sorted_concepts = sorted(linkable_concepts.items(), key=lambda x: len(x[0]), reverse=True)
        
        for concept_lower, concept_original in sorted_concepts:
            # Skip very short concepts
            if len(concept_lower) < 4:
                continue
                
            # Create pattern to match the concept (case insensitive, word boundaries)
            pattern = r'\b' + re.escape(concept_lower) + r'\b'
            
            # Find matches in content
            matches = list(re.finditer(pattern, linked_content.lower()))
            
            if matches and f"[[{concept_original}]]" not in linked_content:
                # Replace first occurrence with link
                match = matches[0]
                start, end = match.span()
                
                # Get the actual text to preserve case
                original_text = linked_content[start:end]
                linked_text = f"[[{concept_original}]]"
                
                # Replace in the actual content
                linked_content = (
                    linked_content[:start] + 
                    linked_text + 
                    linked_content[end:]
                )
                
                links_added.append(concept_original)
        
        # Add strategic links for connection opportunities
        for connection in knowledge_context["connection_opportunities"]:
            concept1 = connection["concept1"]
            concept2 = connection["concept2"]
            
            # If both concepts appear in content, ensure they're linked
            if (concept1.lower() in linked_content.lower() and 
                concept2.lower() in linked_content.lower()):
                
                if f"[[{concept1}]]" not in linked_content:
                    linked_content = re.sub(
                        r'\b' + re.escape(concept1.lower()) + r'\b',
                        f"[[{concept1}]]",
                        linked_content,
                        count=1,
                        flags=re.IGNORECASE
                    )
                    links_added.append(concept1)
                
                if f"[[{concept2}]]" not in linked_content:
                    linked_content = re.sub(
                        r'\b' + re.escape(concept2.lower()) + r'\b', 
                        f"[[{concept2}]]",
                        linked_content,
                        count=1,
                        flags=re.IGNORECASE
                    )
                    links_added.append(concept2)
        
        return {
            "content": linked_content,
            "original_content": content,
            "links_added": links_added,
            "total_links": len(self._extract_all_links(linked_content))
        }
    
    async def _create_connection_bridges(
        self,
        linked_content: Dict[str, Any],
        knowledge_context: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Create bridges between different knowledge domains."""
        logger.debug("✨ Creating connection bridges...")
        
        connection_opportunities = knowledge_context["connection_opportunities"]
        bridges = []
        
        if not connection_opportunities:
            return {"bridges": [], "bridge_content": ""}
        
        # Generate bridge content for key connections
        for connection in connection_opportunities[:3]:  # Limit to top 3 connections
            concept1 = connection["concept1"]
            concept2 = connection["concept2"]
            common_links = connection["common_links"]
            
            messages = [
                LLMMessage(
                    role="user",
                    content=f"""As The Magician ✨, create a connection bridge between these concepts:

Concept 1: {concept1}
Concept 2: {concept2}
Common Connections: {', '.join(common_links)}

Create a brief, insightful explanation (2-3 sentences) that reveals the hidden connection between these concepts. Make it illuminating and magical - help the seeker see how these ideas are fundamentally related.

Use [[bidirectional links]] in your explanation."""
                )
            ]
            
            bridge_content = await self._call_llm(messages, llm_client, temperature=0.9)
            
            bridges.append({
                "concept1": concept1,
                "concept2": concept2,
                "bridge_content": bridge_content,
                "common_links": common_links
            })
        
        # Compile all bridge content
        all_bridge_content = "\n\n".join([
            f"**Connection: {bridge['concept1']} ↔ {bridge['concept2']}**\n{bridge['bridge_content']}"
            for bridge in bridges
        ])
        
        return {
            "bridges": bridges,
            "bridge_content": all_bridge_content
        }
    
    async def _manifest_magical_insights(
        self,
        user_query: str,
        linked_content: Dict[str, Any],
        connection_bridges: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Manifest magical insights about the content creation."""
        logger.debug("✨ Manifesting magical insights...")
        
        content_stats = {
            "total_links": linked_content["total_links"],
            "links_added": len(linked_content["links_added"]),
            "bridges_created": len(connection_bridges["bridges"]),
            "content_length": len(linked_content["content"])
        }
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As The Magician ✨, reflect on the magical transformation you've performed:

Original Query: "{user_query}"
Content Statistics:
- Total [[links]] woven: {content_stats['total_links']}
- New links created: {content_stats['links_added']}
- Connection bridges built: {content_stats['bridges_created']}
- Content length: {content_stats['content_length']} characters

Provide magical insights about:
1. The transformation that occurred
2. The power of the connections created
3. How this content bridges known and unknown
4. Your confidence in this magical creation (0.0-1.0)

Speak with the wisdom and power of The Magician - reveal the magic in the mundane."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client, temperature=0.8)
        
        return {
            "magical_insights": response,
            "reasoning": f"Created {content_stats['total_links']} bidirectional links with {content_stats['bridges_created']} connection bridges",
            "confidence": min(0.95, 0.7 + (content_stats['total_links'] * 0.05))
        }
    
    def _extract_all_links(self, content: str) -> Set[str]:
        """Extract all [[bidirectional links]] from content."""
        pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(pattern, content)
        
        links = set()
        for match in matches:
            # Handle links with aliases: [[target|alias]] -> target
            if '|' in match:
                target = match.split('|')[0].strip()
            else:
                target = match.strip()
            links.add(target)
        
        return links
    
    def _compile_magic_response(
        self,
        user_query: str,
        linked_content: Dict[str, Any],
        connection_bridges: Dict[str, Any],
        magical_insights: Dict[str, Any]
    ) -> str:
        """Compile the final magical response."""
        
        response = f"""✨ **The Magician's Transformation**

**Seeker's Request:** {user_query}

**Magical Creation:**

{linked_content['content']}

---

**Connection Bridges:**

{connection_bridges['bridge_content'] if connection_bridges['bridge_content'] else "The concepts await further exploration to reveal their hidden connections."}

---

**Magical Insights:**

{magical_insights['magical_insights']}

**Transformation Statistics:**
• **Bidirectional Links Woven:** {linked_content['total_links']}
• **New Connections Created:** {len(linked_content['links_added'])}
• **Knowledge Bridges Built:** {len(connection_bridges['bridges'])}

*The knowledge has been transformed through the power of connection. Let Justice now evaluate your understanding.*"""
        
        return response