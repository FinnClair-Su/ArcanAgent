"""
The High Priestess - Cognitive Assessment Agent with Bidirectional Links
MCP Capabilities: assess_cognitive_state, calculate_zpd, monitor_cognitive_load, analyze_knowledge_navigation
Responsibility: All cognitive science related information processing using bidirectional links analysis
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.agents.base_agent import BaseAgent
from backend.mcp import MCPCapability, MCPCapabilityType
from backend.obsidian_vault import VaultManager, BidirectionalLinks, FSRSScheduler
from backend.database.repositories.knowledge_repo import KnowledgeRepository


logger = logging.getLogger(__name__)


class TheHighPriestess(BaseAgent):
    """The High Priestess - Cognitive Assessment Agent with Bidirectional Links"""
    
    def __init__(self):
        super().__init__(
            agent_id="the_high_priestess",
            name="The High Priestess",
            description="Cognitive assessment specialist using ZPD theory, cognitive load analysis, and bidirectional links intelligence"
        )
        self.vault_manager = VaultManager()
        self.bidirectional_links = BidirectionalLinks()
        self.fsrs_scheduler = FSRSScheduler()
        self.knowledge_repo = KnowledgeRepository()
        self.zpd_calculator = ZPDCalculator(self.vault_manager, self.bidirectional_links)
        self.cognitive_load_monitor = CognitiveLoadMonitor(self.vault_manager)
        
    async def _initialize(self):
        """Initialize The High Priestess agent"""
        await self.vault_manager._initialize_vault()
        await self.knowledge_repo.initialize()
        logger.info("The High Priestess cognitive systems initialized")
    
    async def _shutdown(self):
        """Shutdown The High Priestess agent"""
        await self.knowledge_repo.shutdown()
        logger.info("The High Priestess cognitive systems shut down")
    
    async def _register_capabilities(self):
        """Register cognitive capabilities"""
        self.capabilities = [
            MCPCapability(
                name="cognitive_assessment",
                capability_type=MCPCapabilityType.COGNITIVE,
                description="Comprehensive cognitive assessment and diagnosis using bidirectional links analysis",
                methods={
                    "assess_cognitive_state": {
                        "description": "Assess user's current cognitive state with link interaction analysis",
                        "parameters": {
                            "user_id": "string",
                            "session_data": "object",
                            "context": "object"
                        }
                    },
                    "calculate_zpd": {
                        "description": "Calculate Zone of Proximal Development using knowledge network",
                        "parameters": {
                            "user_id": "string",
                            "current_abilities": "object",
                            "target_skills": "array"
                        }
                    },
                    "monitor_cognitive_load": {
                        "description": "Monitor cognitive load with bidirectional links complexity",
                        "parameters": {
                            "user_id": "string",
                            "task_data": "object",
                            "performance_metrics": "object"
                        }
                    },
                    "analyze_learning_style": {
                        "description": "Analyze learning style with link exploration patterns",
                        "parameters": {
                            "user_id": "string",
                            "interaction_history": "array"
                        }
                    },
                    "analyze_knowledge_navigation": {
                        "description": "Analyze how user navigates through knowledge links",
                        "parameters": {
                            "user_id": "string",
                            "navigation_history": "array",
                            "link_patterns": "object"
                        }
                    },
                    "assess_cognitive_readiness": {
                        "description": "Assess readiness for new concepts based on link exploration",
                        "parameters": {
                            "user_id": "string",
                            "target_concept": "string",
                            "current_knowledge_map": "array"
                        }
                    }
                },
                agent_id=self.agent_id,
                version="2.0.0"
            )
        ]
    
    async def assess_cognitive_state(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Assess user's cognitive state with link interaction analysis"""
        user_id = payload.get("user_id")
        session_data = payload.get("session_data", {})
        context = payload.get("context", {})
        
        logger.info(f"Assessing cognitive state for user: {user_id}")
        
        # Retrieve user's cognitive profile from knowledge repo
        cognitive_profile = await self.knowledge_repo.get_user_profile(user_id)
        if not cognitive_profile:
            cognitive_profile = await self.knowledge_repo.create_user_profile(user_id)
        
        # Analyze user's interaction with bidirectional links
        link_interaction_analysis = await self._analyze_link_interactions(user_id, session_data)
        
        # Analyze current session data
        session_analysis = await self._analyze_session_data(session_data)
        
        # Calculate cognitive metrics including link navigation abilities
        cognitive_metrics = {
            "attention_level": session_analysis.get("attention_score", 0.5),
            "processing_speed": session_analysis.get("response_time_score", 0.5),
            "working_memory": session_analysis.get("memory_score", 0.5),
            "cognitive_flexibility": session_analysis.get("flexibility_score", 0.5),
            "meta_cognitive_awareness": session_analysis.get("metacognition_score", 0.5),
            "link_navigation_skill": link_interaction_analysis.get("navigation_score", 0.5),
            "concept_connection_ability": link_interaction_analysis.get("connection_score", 0.5)
        }
        
        # Update cognitive profile with link interaction insights
        await self.knowledge_repo.update_user_profile(user_id, cognitive_metrics)
        
        # Generate assessment report
        assessment = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "cognitive_state": "active",  # active, fatigued, optimal, overloaded
            "cognitive_metrics": cognitive_metrics,
            "link_interaction_analysis": link_interaction_analysis,
            "recommendations": await self._generate_cognitive_recommendations(cognitive_metrics),
            "confidence_level": session_analysis.get("confidence", 0.7)
        }
        
        logger.info(f"Cognitive assessment completed for user: {user_id}")
        return assessment
    
    async def calculate_zpd(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Zone of Proximal Development using knowledge network"""
        user_id = payload.get("user_id")
        current_abilities = payload.get("current_abilities", {})
        target_skills = payload.get("target_skills", [])
        
        logger.info(f"Calculating ZPD for user: {user_id}")
        
        # Get user's cognitive profile
        cognitive_profile = await self.knowledge_repo.get_user_profile(user_id)
        
        # Analyze current knowledge network
        knowledge_network = await self._analyze_user_knowledge_network(user_id, current_abilities)
        
        # Calculate ZPD using cognitive profile, current abilities, and knowledge network
        zpd_analysis = await self.zpd_calculator.calculate_zpd(
            cognitive_profile,
            current_abilities,
            target_skills,
            knowledge_network
        )
        
        zpd_result = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "current_level": zpd_analysis.get("current_level", 0),
            "potential_level": zpd_analysis.get("potential_level", 0),
            "zpd_range": zpd_analysis.get("zpd_range", [0, 0]),
            "recommended_difficulty": zpd_analysis.get("recommended_difficulty", 0.5),
            "support_needed": zpd_analysis.get("support_level", "medium"),
            "optimal_challenge_level": zpd_analysis.get("challenge_level", 0.6),
            "knowledge_network_analysis": knowledge_network
        }
        
        # Store ZPD analysis with link network context
        await self.knowledge_repo.store_zpd_analysis(user_id, zpd_result)
        
        logger.info(f"ZPD calculation completed for user: {user_id}")
        return zpd_result
    
    async def monitor_cognitive_load(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor cognitive load with bidirectional links complexity"""
        user_id = payload.get("user_id")
        task_data = payload.get("task_data", {})
        performance_metrics = payload.get("performance_metrics", {})
        
        logger.info(f"Monitoring cognitive load for user: {user_id}")
        
        # Analyze cognitive load indicators including link complexity
        load_analysis = await self.cognitive_load_monitor.analyze_load(
            task_data,
            performance_metrics
        )
        
        cognitive_load = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "intrinsic_load": load_analysis.get("intrinsic_load", 0.5),
            "extraneous_load": load_analysis.get("extraneous_load", 0.3),
            "germane_load": load_analysis.get("germane_load", 0.4),
            "total_load": load_analysis.get("total_load", 0.6),
            "load_status": load_analysis.get("status", "optimal"),  # optimal, high, overload
            "link_complexity_load": load_analysis.get("link_complexity", 0.3),
            "recommendations": load_analysis.get("recommendations", [])
        }
        
        # Store cognitive load data
        await self.knowledge_repo.store_cognitive_load(user_id, cognitive_load)
        
        # Send notification if overloaded
        if cognitive_load["load_status"] == "overload":
            await self.send_notification(
                target_agent="temperance",
                capability="load_regulation",
                method="reduce_cognitive_load",
                user_id=user_id,
                current_load=cognitive_load["total_load"]
            )
        
        logger.info(f"Cognitive load monitoring completed for user: {user_id}")
        return cognitive_load
    
    async def analyze_learning_style(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze learning style with link exploration patterns"""
        user_id = payload.get("user_id")
        interaction_history = payload.get("interaction_history", [])
        
        logger.info(f"Analyzing learning style for user: {user_id}")
        
        # Analyze interaction patterns including bidirectional links
        style_analysis = await self._analyze_interaction_patterns(interaction_history)
        
        learning_style = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "primary_style": style_analysis.get("primary_style", "visual"),
            "secondary_style": style_analysis.get("secondary_style", "kinesthetic"),
            "style_confidence": style_analysis.get("confidence", 0.7),
            "learning_preferences": style_analysis.get("preferences", {}),
            "adaptation_suggestions": style_analysis.get("suggestions", []),
            "link_exploration_style": style_analysis.get("link_style", "balanced")
        }
        
        # Store learning style analysis
        await self.knowledge_repo.store_learning_style(user_id, learning_style)
        
        logger.info(f"Learning style analysis completed for user: {user_id}")
        return learning_style
    
    async def analyze_knowledge_navigation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how user navigates through knowledge links"""
        user_id = payload.get("user_id")
        navigation_history = payload.get("navigation_history", [])
        link_patterns = payload.get("link_patterns", {})
        
        logger.info(f"Analyzing knowledge navigation for user: {user_id}")
        
        # Analyze navigation patterns
        navigation_analysis = await self._analyze_navigation_patterns(navigation_history)
        
        # Analyze link exploration behavior
        exploration_analysis = await self._analyze_link_exploration(link_patterns)
        
        # Calculate cognitive navigation metrics
        navigation_metrics = {
            "exploration_depth": navigation_analysis.get("depth_score", 0.5),
            "link_following_strategy": navigation_analysis.get("strategy", "random"),
            "concept_connection_rate": exploration_analysis.get("connection_rate", 0.5),
            "knowledge_graph_utilization": exploration_analysis.get("graph_utilization", 0.5),
            "serendipitous_discovery_rate": exploration_analysis.get("discovery_rate", 0.3)
        }
        
        # Generate navigation insights
        insights = await self._generate_navigation_insights(navigation_metrics)
        
        return {
            "user_id": user_id,
            "navigation_metrics": navigation_metrics,
            "exploration_patterns": exploration_analysis,
            "learning_insights": insights,
            "recommendations": await self._recommend_navigation_improvements(navigation_metrics)
        }
    
    async def assess_cognitive_readiness(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Assess readiness for new concepts based on link exploration"""
        user_id = payload.get("user_id")
        target_concept = payload.get("target_concept")
        current_knowledge_map = payload.get("current_knowledge_map", [])
        
        logger.info(f"Assessing cognitive readiness for {target_concept} for user: {user_id}")
        
        # Find the target concept in the vault
        target_notes = await self._find_concept_notes(target_concept)
        if not target_notes:
            return {"error": "Target concept not found in knowledge vault"}
        
        target_note_id = target_notes[0]
        
        # Analyze prerequisite coverage
        prerequisite_coverage = await self._analyze_prerequisite_coverage(
            target_note_id, current_knowledge_map
        )
        
        # Analyze cognitive load for target concept
        cognitive_load_prediction = await self._predict_cognitive_load(
            target_note_id, current_knowledge_map
        )
        
        # Calculate readiness score
        readiness_score = await self._calculate_readiness_score(
            prerequisite_coverage, cognitive_load_prediction
        )
        
        return {
            "user_id": user_id,
            "target_concept": target_concept,
            "readiness_score": readiness_score,
            "prerequisite_coverage": prerequisite_coverage,
            "predicted_cognitive_load": cognitive_load_prediction,
            "recommendations": await self._generate_readiness_recommendations(
                readiness_score, prerequisite_coverage
            ),
            "optimal_learning_path": await self._suggest_optimal_learning_path(
                target_note_id, current_knowledge_map
            )
        }
    
    # Helper methods
    
    async def _analyze_link_interactions(self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's interaction with bidirectional links"""
        link_clicks = session_data.get("link_clicks", [])
        time_on_linked_concepts = session_data.get("time_on_concepts", {})
        
        # Calculate navigation efficiency
        navigation_score = 0.5
        if len(link_clicks) > 0:
            # More link exploration = higher navigation score
            navigation_score = min(len(link_clicks) / 10, 1.0)
        
        # Calculate concept connection ability
        connection_score = 0.5
        if time_on_linked_concepts:
            # Balanced time on concepts indicates good connection understanding
            times = list(time_on_linked_concepts.values())
            if times:
                avg_time = sum(times) / len(times)
                variance = sum((t - avg_time) ** 2 for t in times) / len(times)
                connection_score = max(0, 1 - (variance / (avg_time ** 2)))
        
        return {
            "navigation_score": navigation_score,
            "connection_score": connection_score,
            "exploration_pattern": "systematic" if navigation_score > 0.7 else "random"
        }
    
    async def _analyze_user_knowledge_network(self, user_id: str, current_abilities: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's current knowledge network in the vault"""
        # Find notes related to user's current abilities
        related_notes = []
        for ability in current_abilities.keys():
            notes = await self._find_concept_notes(ability)
            related_notes.extend(notes)
        
        # Analyze the network structure around user's knowledge
        if related_notes:
            network_density = await self._calculate_knowledge_network_density(related_notes)
            coverage_gaps = await self._identify_knowledge_gaps(related_notes)
            
            return {
                "known_concepts_count": len(related_notes),
                "network_density": network_density,
                "coverage_gaps": coverage_gaps,
                "knowledge_clustering": await self._analyze_knowledge_clustering(related_notes)
            }
        
        return {
            "known_concepts_count": 0,
            "network_density": 0,
            "coverage_gaps": [],
            "knowledge_clustering": {}
        }
    
    async def _analyze_session_data(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze session data for cognitive indicators"""
        # Enhanced session analysis with bidirectional links context
        link_interactions = session_data.get("link_interactions", 0)
        average_time_per_concept = session_data.get("avg_time_per_concept", 60)
        concept_switches = session_data.get("concept_switches", 0)
        
        # Calculate attention score based on concept focus
        attention_score = 0.7
        if average_time_per_concept > 30:  # Good focus time
            attention_score += 0.2
        if concept_switches < 5:  # Not too scattered
            attention_score += 0.1
        
        # Calculate processing speed based on link navigation
        response_time_score = 0.8
        if link_interactions > 3:  # Active exploration
            response_time_score += 0.1
        
        return {
            "attention_score": min(attention_score, 1.0),
            "response_time_score": min(response_time_score, 1.0),
            "memory_score": 0.6,
            "flexibility_score": min(link_interactions / 5, 1.0),  # Based on link exploration
            "metacognition_score": 0.5,
            "confidence": 0.8
        }
    
    async def _generate_cognitive_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate cognitive recommendations including link navigation"""
        recommendations = []
        
        if metrics.get("attention_level", 0) < 0.5:
            recommendations.append("Consider taking breaks to improve attention")
        
        if metrics.get("cognitive_flexibility", 0) < 0.5:
            recommendations.append("Try varied learning approaches to improve flexibility")
        
        if metrics.get("link_navigation_skill", 0) < 0.5:
            recommendations.append("Explore more bidirectional links to improve concept connections")
        
        if metrics.get("concept_connection_ability", 0) < 0.5:
            recommendations.append("Spend more time understanding relationships between concepts")
        
        return recommendations
    
    async def _find_concept_notes(self, concept: str) -> List[str]:
        """Find notes related to a concept in the vault"""
        matching_notes = []
        for note_id, note_data in self.vault_manager.note_index.items():
            title = note_data.get("title", "").lower()
            content = note_data.get("content", "").lower()
            if concept.lower() in title or concept.lower() in content:
                matching_notes.append(note_id)
        return matching_notes[:5]  # Return top 5 matches
    
    async def _analyze_prerequisite_coverage(self, target_note_id: str, current_knowledge: List[str]) -> Dict[str, Any]:
        """Analyze how well prerequisites are covered"""
        # Get incoming links to the target note (these could be prerequisites)
        incoming_links = self.bidirectional_links.get_incoming_links(target_note_id)
        
        # Check how many prerequisites are in current knowledge
        known_prerequisites = 0
        for link in incoming_links:
            link_note = self.vault_manager.note_index.get(link)
            if link_note:
                title = link_note.get("title", "")
                if any(knowledge.lower() in title.lower() for knowledge in current_knowledge):
                    known_prerequisites += 1
        
        coverage_ratio = known_prerequisites / max(len(incoming_links), 1)
        
        return {
            "total_prerequisites": len(incoming_links),
            "known_prerequisites": known_prerequisites,
            "coverage_ratio": coverage_ratio,
            "missing_prerequisites": len(incoming_links) - known_prerequisites
        }
    
    async def _predict_cognitive_load(self, target_note_id: str, current_knowledge: List[str]) -> Dict[str, Any]:
        """Predict cognitive load for learning target concept"""
        note_data = self.vault_manager.note_index.get(target_note_id)
        if not note_data:
            return {"load_level": 0.5}
        
        # Get complexity indicators
        content_length = len(note_data.get("content", ""))
        outgoing_links = len(self.bidirectional_links.get_outgoing_links(target_note_id))
        incoming_links = len(self.bidirectional_links.get_incoming_links(target_note_id))
        
        # Calculate intrinsic load based on content complexity
        intrinsic_load = min(content_length / 1000, 1.0)  # Normalize by content length
        
        # Calculate germane load based on connections
        germane_load = min((outgoing_links + incoming_links) / 20, 1.0)
        
        # Calculate extraneous load based on missing prerequisites
        prerequisite_coverage = await self._analyze_prerequisite_coverage(target_note_id, current_knowledge)
        extraneous_load = 1 - prerequisite_coverage["coverage_ratio"]
        
        total_load = (intrinsic_load + germane_load + extraneous_load) / 3
        
        return {
            "intrinsic_load": intrinsic_load,
            "germane_load": germane_load,
            "extraneous_load": extraneous_load,
            "total_load": total_load,
            "load_level": "high" if total_load > 0.7 else "medium" if total_load > 0.4 else "low"
        }
    
    async def _calculate_readiness_score(self, prerequisite_coverage: Dict[str, Any], 
                                       cognitive_load: Dict[str, Any]) -> float:
        """Calculate overall readiness score"""
        coverage_score = prerequisite_coverage["coverage_ratio"]
        load_score = 1 - cognitive_load["total_load"]  # Invert load (lower load = higher readiness)
        
        # Weight coverage more heavily
        readiness_score = (coverage_score * 0.7) + (load_score * 0.3)
        
        return min(max(readiness_score, 0), 1)  # Clamp to 0-1
    
    async def _generate_readiness_recommendations(self, readiness_score: float, 
                                                prerequisite_coverage: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on readiness assessment"""
        recommendations = []
        
        if readiness_score < 0.5:
            recommendations.append("Consider learning prerequisite concepts first")
        
        if prerequisite_coverage["coverage_ratio"] < 0.6:
            recommendations.append(f"Focus on the {prerequisite_coverage['missing_prerequisites']} missing prerequisite concepts")
        
        if readiness_score > 0.8:
            recommendations.append("You're ready to learn this concept!")
        
        return recommendations
    
    async def _suggest_optimal_learning_path(self, target_note_id: str, current_knowledge: List[str]) -> List[str]:
        """Suggest optimal learning path to reach target concept"""
        # Get prerequisites that need to be learned
        incoming_links = self.bidirectional_links.get_incoming_links(target_note_id)
        
        learning_path = []
        for link in incoming_links:
            link_note = self.vault_manager.note_index.get(link)
            if link_note:
                title = link_note.get("title", "")
                if not any(knowledge.lower() in title.lower() for knowledge in current_knowledge):
                    learning_path.append(title)
        
        # Add target concept at the end
        target_note = self.vault_manager.note_index.get(target_note_id)
        if target_note:
            learning_path.append(target_note.get("title", ""))
        
        return learning_path
    
    # Additional helper methods (simplified for space)
    
    async def _analyze_navigation_patterns(self, navigation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not navigation_history:
            return {"depth_score": 0, "strategy": "none"}
        
        max_depth = max(nav.get("depth", 0) for nav in navigation_history)
        avg_depth = sum(nav.get("depth", 0) for nav in navigation_history) / len(navigation_history)
        strategy = "systematic" if avg_depth > 2 else "surface"
        
        return {"depth_score": min(avg_depth / 3, 1.0), "strategy": strategy}
    
    async def _analyze_link_exploration(self, link_patterns: Dict[str, Any]) -> Dict[str, Any]:
        total_links = link_patterns.get("total_available", 1)
        followed = link_patterns.get("followed", 0)
        unique_concepts = link_patterns.get("unique_concepts", 0)
        
        return {
            "connection_rate": followed / max(total_links, 1),
            "discovery_rate": unique_concepts / max(followed, 1) if followed > 0 else 0,
            "graph_utilization": min(unique_concepts / 10, 1.0)
        }
    
    async def _generate_navigation_insights(self, navigation_metrics: Dict[str, Any]) -> List[str]:
        insights = []
        exploration_depth = navigation_metrics.get("exploration_depth", 0)
        
        if exploration_depth < 0.3:
            insights.append("User tends to stay on surface-level concepts")
        elif exploration_depth > 0.7:
            insights.append("User demonstrates deep conceptual exploration")
        
        return insights
    
    async def _recommend_navigation_improvements(self, navigation_metrics: Dict[str, Any]) -> List[str]:
        recommendations = []
        
        if navigation_metrics.get("exploration_depth", 0) < 0.5:
            recommendations.append("Try following more bidirectional links to discover deeper connections")
        
        return recommendations
    
    async def _calculate_knowledge_network_density(self, note_ids: List[str]) -> float:
        if len(note_ids) < 2:
            return 0
        
        total_possible = len(note_ids) * (len(note_ids) - 1) / 2
        actual_connections = 0
        
        for i, note1 in enumerate(note_ids):
            for note2 in note_ids[i+1:]:
                outgoing1 = self.bidirectional_links.get_outgoing_links(note1)
                if note2 in outgoing1:
                    actual_connections += 1
        
        return actual_connections / total_possible if total_possible > 0 else 0
    
    async def _identify_knowledge_gaps(self, note_ids: List[str]) -> List[str]:
        linked_concepts = set()
        for note_id in note_ids:
            outgoing = self.bidirectional_links.get_outgoing_links(note_id)
            linked_concepts.update(outgoing)
        
        gaps = linked_concepts - set(note_ids)
        gap_titles = []
        for gap_id in gaps:
            note_data = self.vault_manager.note_index.get(gap_id)
            if note_data:
                gap_titles.append(note_data.get("title", ""))
        
        return gap_titles[:5]
    
    async def _analyze_knowledge_clustering(self, note_ids: List[str]) -> Dict[str, Any]:
        clusters = {}
        for note_id in note_ids:
            note_data = self.vault_manager.note_index.get(note_id)
            if note_data:
                tags = note_data.get("frontmatter", {}).get("tags", [])
                for tag in tags:
                    if tag not in clusters:
                        clusters[tag] = []
                    clusters[tag].append(note_data.get("title", ""))
        
        return {
            "cluster_count": len(clusters),
            "largest_cluster": max(clusters.values(), key=len) if clusters else [],
            "cluster_distribution": {k: len(v) for k, v in clusters.items()}
        }
    
    async def _analyze_interaction_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced interaction analysis with bidirectional links"""
        link_interactions = [i for i in interactions if i.get("type") == "link_click"]
        
        if link_interactions:
            avg_links_per_session = len(link_interactions) / max(len(set(i.get("session_id") for i in interactions)), 1)
            link_depth_preference = sum(i.get("link_depth", 1) for i in link_interactions) / len(link_interactions)
        else:
            avg_links_per_session = 0
            link_depth_preference = 1
        
        if avg_links_per_session > 5 and link_depth_preference > 2:
            primary_style = "exploratory"
        elif avg_links_per_session < 2:
            primary_style = "focused"
        else:
            primary_style = "balanced"
        
        return {
            "primary_style": primary_style,
            "secondary_style": "kinesthetic",
            "confidence": 0.8,
            "preferences": {
                "exploratory": min(avg_links_per_session / 5, 1.0),
                "focused": 1 - min(avg_links_per_session / 5, 1.0),
                "link_depth": min(link_depth_preference / 3, 1.0)
            },
            "suggestions": ["Continue exploring bidirectional links"] if primary_style == "exploratory" else ["Try following more links"],
            "link_style": primary_style
        }


class ZPDCalculator:
    """Zone of Proximal Development calculator with bidirectional links support"""
    
    def __init__(self, vault_manager, bidirectional_links):
        self.vault = vault_manager
        self.links = bidirectional_links
    
    async def calculate_zpd(self, cognitive_profile: Dict[str, Any], current_abilities: Dict[str, Any], 
                          target_skills: List[str], knowledge_network: Dict[str, Any] = None) -> Dict[str, Any]:
        """Calculate ZPD based on cognitive profile, abilities, and knowledge network"""
        current_level = sum(current_abilities.values()) / len(current_abilities) if current_abilities else 0
        
        # Adjust potential level based on knowledge network density
        network_bonus = 0
        if knowledge_network:
            network_density = knowledge_network.get("network_density", 0)
            network_bonus = network_density * 0.2  # Up to 20% bonus for well-connected knowledge
        
        potential_level = min(current_level + 0.3 + network_bonus, 1.0)
        
        return {
            "current_level": current_level,
            "potential_level": potential_level,
            "zpd_range": [current_level, potential_level],
            "recommended_difficulty": (current_level + potential_level) / 2,
            "support_level": "medium",
            "challenge_level": potential_level - 0.1,
            "network_enhancement": network_bonus
        }


class CognitiveLoadMonitor:
    """Cognitive load monitoring system with bidirectional links complexity"""
    
    def __init__(self, vault_manager):
        self.vault = vault_manager
    
    async def analyze_load(self, task_data: Dict[str, Any], performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cognitive load including bidirectional links complexity"""
        task_complexity = task_data.get("complexity", 0.5)
        performance_quality = performance_metrics.get("quality", 0.7)
        
        # Calculate link complexity load
        links_involved = task_data.get("links_involved", 0)
        link_complexity = min(links_involved / 10, 0.5)  # Max 50% load from links
        
        intrinsic_load = task_complexity + link_complexity
        extraneous_load = max(0, 1 - performance_quality - task_complexity)
        germane_load = min(performance_quality, 1 - intrinsic_load - extraneous_load)
        total_load = intrinsic_load + extraneous_load + germane_load
        
        status = "optimal"
        if total_load > 0.8:
            status = "overload"
        elif total_load > 0.6:
            status = "high"
        
        recommendations = []
        if link_complexity > 0.3:
            recommendations.append("Consider reducing the number of linked concepts")
        if status == "overload":
            recommendations.append("Reduce task complexity")
        
        return {
            "intrinsic_load": intrinsic_load,
            "extraneous_load": extraneous_load,
            "germane_load": germane_load,
            "total_load": total_load,
            "link_complexity": link_complexity,
            "status": status,
            "recommendations": recommendations
        }