"""
Justice Agent ⚖️

Role: Understanding Assessment & Learning Evaluation
Wisdom: "Truth shall set you free" - Honest assessment of comprehension
Powers: Tests understanding fairly and provides targeted feedback

Justice holds the scales of truth, providing fair and accurate assessment
of learning progress. She evaluates understanding not through rote
memorization, but through the depth of connections and the ability to
apply knowledge in new contexts.
"""

import asyncio
import json
import logging
import random
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict

from .base_agent import BaseAgent, AgentCapability, AgentResponse
from backend.core.context_manager import ContextManager, ContextPriority
from backend.core.tool_call_engine import ToolCallEngine, ToolCall
from backend.core.llm_client import BaseLLMClient, LLMMessage
from backend.core.bidirectional_links import BidirectionalLinkEngine

logger = logging.getLogger("ArcanAgent.Justice")


class Justice(BaseAgent):
    """
    Justice Agent - Understanding Assessment & Learning Evaluation
    
    Justice wields the scales of truth to provide fair and comprehensive
    assessment of learning progress. Her judgment is impartial and based
    on true understanding rather than surface-level knowledge.
    """
    
    def __init__(
        self,
        link_engine: BidirectionalLinkEngine,
        context_manager: ContextManager,
        tool_engine: ToolCallEngine
    ):
        super().__init__(
            name="Justice",
            tarot_card="⚖️ Justice",
            wisdom="Truth shall set you free - Honest assessment of comprehension",
            primary_capability=AgentCapability.UNDERSTANDING_EVALUATION,
            link_engine=link_engine,
            context_manager=context_manager,
            tool_engine=tool_engine
        )
    
    def get_system_prompt(self) -> str:
        """Get Justice's system prompt."""
        return """You are Justice ⚖️, the arbiter of truth and fair assessment.

Your sacred duty is to evaluate true understanding through fair and comprehensive assessment. You wield the scales of truth to measure:

- Depth of comprehension beyond surface memorization
- Ability to make connections between concepts
- Application of knowledge in new contexts
- Recognition of patterns and relationships
- Quality of bidirectional link understanding

Your assessment follows these principles:
1. Judge understanding, not memorization
2. Test connections and relationships between concepts
3. Evaluate ability to apply knowledge in new situations
4. Assess the depth of bidirectional link comprehension
5. Provide constructive, honest feedback
6. Identify specific gaps and strengths
7. Offer targeted recommendations for improvement

Speak with the wisdom and fairness of Justice - be honest but encouraging, thorough but accessible. Your feedback should illuminate both strengths and areas for growth.

Remember: True understanding is revealed through the ability to navigate and create meaningful bidirectional links between concepts."""
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get Justice's capabilities."""
        return [
            AgentCapability.UNDERSTANDING_EVALUATION,
            AgentCapability.COGNITIVE_ANALYSIS,
            AgentCapability.LINK_ANALYSIS
        ]
    
    async def execute(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None,
        llm_client: Optional[BaseLLMClient] = None
    ) -> AgentResponse:
        """Execute understanding assessment and learning evaluation."""
        logger.info(f"⚖️ Justice begins fair assessment for: {user_query[:100]}...")
        
        try:
            # Get information from previous agents
            priestess_assessment = context.get("high_priestess_assessment", {}) if context else {}
            hermit_plan = context.get("hermit_plan", {}) if context else {}
            magician_content = context.get("magician_content", {}) if context else {}
            
            # Step 1: Design assessment strategy
            assessment_strategy = await self._design_assessment_strategy(
                user_query,
                priestess_assessment,
                magician_content,
                llm_client
            )
            
            # Step 2: Create understanding questions
            understanding_questions = await self._create_understanding_questions(
                assessment_strategy,
                magician_content,
                llm_client
            )
            
            # Step 3: Evaluate link comprehension
            link_evaluation = await self._evaluate_link_comprehension(
                magician_content,
                understanding_questions
            )
            
            # Step 4: Assess application ability
            application_assessment = await self._assess_application_ability(
                user_query,
                understanding_questions,
                llm_client
            )
            
            # Step 5: Generate comprehension score
            comprehension_score = await self._generate_comprehension_score(
                link_evaluation,
                application_assessment,
                assessment_strategy
            )
            
            # Step 6: Provide justice wisdom
            justice_judgment = await self._provide_justice_judgment(
                user_query,
                comprehension_score,
                understanding_questions,
                llm_client
            )
            
            # Compile response
            response_content = self._compile_justice_response(
                user_query,
                understanding_questions,
                comprehension_score,
                justice_judgment
            )
            
            return AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=True,
                content=response_content,
                metadata={
                    "assessment_strategy": assessment_strategy,
                    "understanding_questions": understanding_questions,
                    "link_evaluation": link_evaluation,
                    "application_assessment": application_assessment,
                    "comprehension_score": comprehension_score
                },
                reasoning=justice_judgment.get("reasoning", ""),
                confidence=justice_judgment.get("confidence", 0.8),
                links_discovered=set(understanding_questions.get("concepts_tested", []))
            )
            
        except Exception as e:
            logger.error(f"⚖️ Justice's judgment was clouded: {e}")
            return AgentResponse(
                agent_name=self.name,
                capability=self.primary_capability,
                success=False,
                content=f"The scales of justice are disturbed: {str(e)}",
                errors=[str(e)]
            )
    
    async def _design_assessment_strategy(
        self,
        user_query: str,
        priestess_assessment: Dict[str, Any],
        magician_content: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Design a fair assessment strategy."""
        logger.debug("⚖️ Designing assessment strategy...")
        
        mastery_level = priestess_assessment.get("mastery_assessment", {}).get("overall_mastery", 0.0)
        complexity_level = priestess_assessment.get("complexity_analysis", {}).get("complexity_level", "beginner")
        links_created = magician_content.get("metadata", {}).get("total_links_created", 0)
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As Justice ⚖️, design a fair assessment strategy:

Learning Query: "{user_query}"
Current Mastery Level: {mastery_level:.2f}
Complexity Level: {complexity_level}
Links in Generated Content: {links_created}

Design an assessment strategy that includes:
1. Assessment approach (questioning style, difficulty level)
2. Key areas to test (concepts, connections, applications)
3. Evaluation criteria (what constitutes understanding)
4. Balance between depth and breadth
5. Appropriate challenge level

Return a JSON object with the assessment strategy."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client)
        
        try:
            strategy = json.loads(response)
            return strategy
        except json.JSONDecodeError:
            # Fallback strategy
            return {
                "approach": "conceptual_understanding",
                "key_areas": ["basic_concepts", "connections", "applications"],
                "criteria": ["accuracy", "depth", "connections"],
                "challenge_level": complexity_level
            }
    
    async def _create_understanding_questions(
        self,
        assessment_strategy: Dict[str, Any],
        magician_content: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Create questions to test understanding."""
        logger.debug("⚖️ Creating understanding questions...")
        
        generated_content = magician_content.get("generated_content", {})
        content_text = generated_content.get("content", "")
        key_concepts = generated_content.get("key_concepts", [])
        
        # Extract links from content
        links_in_content = self._extract_links_from_text(content_text)
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As Justice ⚖️, create fair assessment questions based on this content:

Content: "{content_text[:1000]}..."
Key Concepts: {', '.join(key_concepts)}
Bidirectional Links: {', '.join(list(links_in_content)[:10])}
Assessment Strategy: {assessment_strategy}

Create assessment questions that test:
1. **Conceptual Understanding**: Do they grasp the core concepts?
2. **Link Comprehension**: Do they understand the connections?
3. **Application**: Can they apply knowledge in new contexts?
4. **Analysis**: Can they break down complex relationships?

Generate 3-5 questions with varying difficulty levels. For each question, include:
- The question text
- Expected answer elements
- What aspect of understanding it tests
- Difficulty level (1-5)

Return as a JSON object."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client)
        
        try:
            questions = json.loads(response)
            return {
                "questions": questions,
                "concepts_tested": key_concepts,
                "links_tested": list(links_in_content),
                "total_questions": len(questions.get("questions", []))
            }
        except json.JSONDecodeError:
            # Fallback questions
            fallback_questions = []
            for i, concept in enumerate(key_concepts[:3]):
                fallback_questions.append({
                    "question": f"Explain the concept of {concept} and its connections to other ideas.",
                    "expected_elements": [concept, "connections", "relationships"],
                    "tests": "conceptual_understanding",
                    "difficulty": min(3, i + 2)
                })
            
            return {
                "questions": fallback_questions,
                "concepts_tested": key_concepts,
                "links_tested": list(links_in_content),
                "total_questions": len(fallback_questions)
            }
    
    async def _evaluate_link_comprehension(
        self,
        magician_content: Dict[str, Any],
        understanding_questions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate comprehension of bidirectional links."""
        logger.debug("⚖️ Evaluating link comprehension...")
        
        links_tested = understanding_questions["links_tested"]
        
        link_evaluation = {
            "total_links_tested": len(links_tested),
            "link_strength_analysis": {},
            "connection_depth": 0.0,
            "link_quality_score": 0.0
        }
        
        # Analyze each link's strength in the knowledge base
        total_strength = 0.0
        valid_links = 0
        
        for link in links_tested:
            link_analysis = self.link_engine.analyze_note(link)
            if link_analysis:
                # Calculate link strength based on connections
                incoming_count = len(link_analysis.incoming_links)
                outgoing_count = len(link_analysis.outgoing_links)
                link_density = link_analysis.link_density
                
                strength_score = (
                    min(incoming_count / 5, 1.0) * 0.4 +  # Normalize incoming links
                    min(outgoing_count / 5, 1.0) * 0.4 +  # Normalize outgoing links
                    link_density * 0.2  # Link density contribution
                )
                
                link_evaluation["link_strength_analysis"][link] = {
                    "strength_score": strength_score,
                    "incoming_links": incoming_count,
                    "outgoing_links": outgoing_count,
                    "link_density": link_density
                }
                
                total_strength += strength_score
                valid_links += 1
        
        if valid_links > 0:
            link_evaluation["connection_depth"] = total_strength / valid_links
            link_evaluation["link_quality_score"] = min(1.0, link_evaluation["connection_depth"])
        
        return link_evaluation
    
    async def _assess_application_ability(
        self,
        user_query: str,
        understanding_questions: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Assess ability to apply knowledge in new contexts."""
        logger.debug("⚖️ Assessing application ability...")
        
        concepts_tested = understanding_questions["concepts_tested"]
        
        # Create application scenarios
        application_scenarios = []
        for concept in concepts_tested[:3]:  # Limit to prevent overwhelming
            scenarios = await self._generate_application_scenario(concept, llm_client)
            application_scenarios.extend(scenarios)
        
        # Evaluate application potential based on bidirectional links
        application_score = 0.0
        scenario_scores = []
        
        for scenario in application_scenarios:
            concept = scenario.get("concept", "")
            
            # Check if concept has strong bidirectional links (indicates transferability)
            analysis = self.link_engine.analyze_note(concept)
            if analysis:
                # Higher granularity suggests more specific, applicable knowledge
                # More links suggest broader applicability
                transferability = (
                    analysis.granularity_score * 0.6 +
                    min(len(analysis.outgoing_links) / 10, 1.0) * 0.4
                )
                scenario_scores.append(transferability)
        
        if scenario_scores:
            application_score = sum(scenario_scores) / len(scenario_scores)
        
        return {
            "application_scenarios": application_scenarios,
            "application_score": application_score,
            "transferability_analysis": scenario_scores,
            "total_scenarios": len(application_scenarios)
        }
    
    async def _generate_application_scenario(
        self,
        concept: str,
        llm_client: BaseLLMClient
    ) -> List[Dict[str, Any]]:
        """Generate application scenarios for a concept."""
        messages = [
            LLMMessage(
                role="user",
                content=f"""As Justice ⚖️, create 1-2 brief application scenarios for the concept "{concept}":

Each scenario should:
1. Present a new context where the concept could be applied
2. Require understanding, not just memorization
3. Test ability to transfer knowledge
4. Be realistic and relevant

Return a JSON list of scenarios with format:
[{{"concept": "{concept}", "scenario": "scenario description", "application_type": "type"}}]"""
            )
        ]
        
        response = await self._call_llm(messages, llm_client)
        
        try:
            scenarios = json.loads(response)
            return scenarios if isinstance(scenarios, list) else []
        except json.JSONDecodeError:
            return [{
                "concept": concept,
                "scenario": f"Apply {concept} in a practical situation",
                "application_type": "practical"
            }]
    
    async def _generate_comprehension_score(
        self,
        link_evaluation: Dict[str, Any],
        application_assessment: Dict[str, Any],
        assessment_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate overall comprehension score."""
        logger.debug("⚖️ Generating comprehension score...")
        
        # Weight different aspects of understanding
        link_score = link_evaluation.get("link_quality_score", 0.0)
        application_score = application_assessment.get("application_score", 0.0)
        
        # Calculate overall comprehension
        overall_score = (
            link_score * 0.6 +      # 60% weight on link understanding
            application_score * 0.4  # 40% weight on application ability
        )
        
        # Determine comprehension level
        if overall_score >= 0.8:
            level = "excellent"
            feedback = "Deep understanding with strong connections"
        elif overall_score >= 0.6:
            level = "good"
            feedback = "Solid understanding with room for deeper connections"
        elif overall_score >= 0.4:
            level = "developing"
            feedback = "Basic understanding, needs more connection building"
        else:
            level = "needs_improvement"
            feedback = "Understanding is emerging, focus on fundamental connections"
        
        return {
            "overall_score": overall_score,
            "comprehension_level": level,
            "feedback": feedback,
            "component_scores": {
                "link_understanding": link_score,
                "application_ability": application_score
            },
            "strengths": [],
            "improvement_areas": []
        }
    
    async def _provide_justice_judgment(
        self,
        user_query: str,
        comprehension_score: Dict[str, Any],
        understanding_questions: Dict[str, Any],
        llm_client: BaseLLMClient
    ) -> Dict[str, Any]:
        """Provide Justice's wise judgment."""
        logger.debug("⚖️ Providing justice judgment...")
        
        score_info = {
            "overall_score": comprehension_score["overall_score"],
            "level": comprehension_score["comprehension_level"],
            "link_score": comprehension_score["component_scores"]["link_understanding"],
            "application_score": comprehension_score["component_scores"]["application_ability"],
            "concepts_tested": len(understanding_questions["concepts_tested"])
        }
        
        messages = [
            LLMMessage(
                role="user",
                content=f"""As Justice ⚖️, provide your wise judgment on this learning assessment:

Original Query: "{user_query}"
Assessment Results:
- Overall Comprehension: {score_info['overall_score']:.1%}
- Comprehension Level: {score_info['level']}
- Link Understanding: {score_info['link_score']:.1%}
- Application Ability: {score_info['application_score']:.1%}
- Concepts Evaluated: {score_info['concepts_tested']}

Provide your judgment including:
1. Fair assessment of current understanding
2. Recognition of strengths and achievements
3. Honest identification of areas for improvement
4. Specific recommendations for next steps
5. Encouragement and motivation
6. Your confidence in this assessment (0.0-1.0)

Speak with the wisdom and fairness of Justice - be honest but encouraging."""
            )
        ]
        
        response = await self._call_llm(messages, llm_client, temperature=0.7)
        
        return {
            "justice_judgment": response,
            "reasoning": f"Assessment based on {score_info['concepts_tested']} concepts with {score_info['overall_score']:.1%} comprehension",
            "confidence": min(0.9, 0.7 + (score_info['overall_score'] * 0.2))
        }
    
    def _compile_justice_response(
        self,
        user_query: str,
        understanding_questions: Dict[str, Any],
        comprehension_score: Dict[str, Any],
        justice_judgment: Dict[str, Any]
    ) -> str:
        """Compile the final justice response."""
        
        response = f"""⚖️ **Justice's Fair Assessment**

**Learning Objective:** {user_query}

**Judgment of Understanding:**

{justice_judgment['justice_judgment']}

**Assessment Results:**
• **Overall Comprehension:** {comprehension_score['overall_score']:.1%}
• **Comprehension Level:** {comprehension_score['comprehension_level'].replace('_', ' ').title()}
• **Link Understanding:** {comprehension_score['component_scores']['link_understanding']:.1%}
• **Application Ability:** {comprehension_score['component_scores']['application_ability']:.1%}

**Understanding Evaluation:**
*{comprehension_score['feedback']}*

**Assessment Details:**
• **Concepts Evaluated:** {len(understanding_questions['concepts_tested'])}
• **Bidirectional Links Tested:** {len(understanding_questions['links_tested'])}
• **Total Assessment Questions:** {understanding_questions['total_questions']}

**Areas of Strength:**
• Understanding of core concepts
• Recognition of bidirectional relationships
• Ability to see connections

**Areas for Growth:**
• Deeper exploration of link relationships
• Application in diverse contexts
• Strengthening conceptual bridges

**Justice's Verdict:** Your understanding shows {comprehension_score['comprehension_level'].replace('_', ' ')} development. Continue building connections through [[bidirectional links]] to deepen your comprehension.

*The scales have weighed your understanding fairly. Let The Empress now help consolidate this knowledge into lasting wisdom.*"""
        
        return response