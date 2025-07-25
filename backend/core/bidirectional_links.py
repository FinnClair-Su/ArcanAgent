"""
Bidirectional Links Engine

Core engine implementing the philosophy "Bidirectional Linking is All You Need"
for ArcanAgent's knowledge management system. This engine replaces complex
graph databases with elegant file-system based bidirectional linking.

Mathematical Foundation:
- Granularity = f(incoming_links, outgoing_links)  
- Context_Quality = Σ(shortest_paths) × neighborhood_expansion
- Learning_Readiness = |prerequisites ∩ known_concepts| / |prerequisites|
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, deque
import frontmatter
import logging

logger = logging.getLogger("ArcanAgent.BidirectionalLinks")


@dataclass
class LinkAnalysis:
    """Analysis results for a single note's link structure."""
    note_id: str
    outgoing_links: Set[str]
    incoming_links: Set[str]
    link_density: float
    granularity_score: float
    context_layers: Dict[str, str]  # full, summary, title


@dataclass
class PathInfo:
    """Information about a path between two notes."""
    path: List[str]
    distance: int
    cognitive_weight: float
    learning_readiness: float


class BidirectionalLinkEngine:
    """
    Core engine for bidirectional link analysis and management.
    
    Implements the "Bidirectional Linking is All You Need" philosophy by:
    1. Parsing markdown files for [[wiki-style]] links
    2. Building bidirectional link network in memory
    3. Calculating link density and granularity scores
    4. Providing context-aware content selection
    5. Finding optimal learning paths between concepts
    """
    
    def __init__(self, knowledge_base_path: str):
        """Initialize the bidirectional link engine."""
        self.knowledge_base_path = Path(knowledge_base_path)
        self.notes_path = self.knowledge_base_path / "notes"
        
        # Core data structures
        self.link_graph: Dict[str, Set[str]] = defaultdict(set)  # outgoing links
        self.reverse_links: Dict[str, Set[str]] = defaultdict(set)  # incoming links
        self.note_metadata: Dict[str, Dict[str, Any]] = {}
        self.note_content: Dict[str, str] = {}
        
        # Analysis cache
        self._analysis_cache: Dict[str, LinkAnalysis] = {}
        self._path_cache: Dict[Tuple[str, str], PathInfo] = {}
        
        logger.info(f"Initialized BidirectionalLinkEngine with knowledge base: {knowledge_base_path}")
    
    def refresh_knowledge_base(self) -> None:
        """
        Refresh the entire knowledge base by re-reading all markdown files.
        This should be called when files are added, modified, or deleted.
        """
        logger.info("Refreshing knowledge base...")
        
        # Clear existing data
        self.link_graph.clear()
        self.reverse_links.clear()
        self.note_metadata.clear()
        self.note_content.clear()
        self._analysis_cache.clear()
        self._path_cache.clear()
        
        # Scan for all markdown files
        if not self.notes_path.exists():
            logger.warning(f"Notes directory does not exist: {self.notes_path}")
            return
        
        markdown_files = list(self.notes_path.rglob("*.md"))
        logger.info(f"Found {len(markdown_files)} markdown files")
        
        # Process each file
        for file_path in markdown_files:
            try:
                self._process_markdown_file(file_path)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        # Build reverse link index
        self._build_reverse_links()
        
        logger.info(f"Knowledge base refreshed: {len(self.note_metadata)} notes, {sum(len(links) for links in self.link_graph.values())} links")
    
    def _process_markdown_file(self, file_path: Path) -> None:
        """Process a single markdown file and extract metadata and links."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Generate note ID from file path (relative to notes directory)
            note_id = str(file_path.relative_to(self.notes_path)).replace('.md', '')
            
            # Extract metadata
            metadata = dict(post.metadata)
            if 'title' not in metadata:
                metadata['title'] = file_path.stem
            
            self.note_metadata[note_id] = metadata
            self.note_content[note_id] = post.content
            
            # Extract outgoing links using regex
            outgoing_links = self._extract_wiki_links(post.content)
            self.link_graph[note_id] = outgoing_links
            
            logger.debug(f"Processed {note_id}: {len(outgoing_links)} outgoing links")
            
        except Exception as e:
            logger.error(f"Error processing markdown file {file_path}: {e}")
    
    def _extract_wiki_links(self, content: str) -> Set[str]:
        """Extract [[wiki-style]] links from markdown content."""
        pattern = r'\[\[([^\]]+)\]\]'
        matches = re.findall(pattern, content)
        
        # Clean and normalize link targets
        links = set()
        for match in matches:
            # Handle links with aliases: [[target|alias]] -> target
            if '|' in match:
                target = match.split('|')[0].strip()
            else:
                target = match.strip()
            
            # Normalize to note ID format
            target = target.replace(' ', '_').lower()
            links.add(target)
        
        return links
    
    def _build_reverse_links(self) -> None:
        """Build the reverse link index (incoming links)."""
        for source_note, targets in self.link_graph.items():
            for target_note in targets:
                self.reverse_links[target_note].add(source_note)
    
    def analyze_note(self, note_id: str, force_refresh: bool = False) -> Optional[LinkAnalysis]:
        """
        Perform comprehensive link analysis for a specific note.
        
        Args:
            note_id: The note to analyze
            force_refresh: Force recalculation even if cached
            
        Returns:
            LinkAnalysis object with complete analysis results
        """
        if not force_refresh and note_id in self._analysis_cache:
            return self._analysis_cache[note_id]
        
        if note_id not in self.note_metadata:
            logger.warning(f"Note not found: {note_id}")
            return None
        
        outgoing = self.link_graph.get(note_id, set())
        incoming = self.reverse_links.get(note_id, set())
        
        # Calculate link density (total connections / possible connections)
        total_notes = len(self.note_metadata)
        if total_notes <= 1:
            link_density = 0.0
        else:
            total_links = len(outgoing) + len(incoming)
            max_possible = (total_notes - 1) * 2  # bidirectional
            link_density = total_links / max_possible
        
        # Calculate granularity score based on mathematical formula
        granularity_score = self._calculate_granularity(len(incoming), len(outgoing))
        
        # Generate context layers
        context_layers = self._generate_context_layers(note_id)
        
        analysis = LinkAnalysis(
            note_id=note_id,
            outgoing_links=outgoing,
            incoming_links=incoming,
            link_density=link_density,
            granularity_score=granularity_score,
            context_layers=context_layers
        )
        
        # Cache the analysis
        self._analysis_cache[note_id] = analysis
        
        return analysis
    
    def _calculate_granularity(self, incoming_count: int, outgoing_count: int) -> float:
        """
        Calculate granularity score based on the mathematical formula:
        Granularity = f(incoming_links, outgoing_links)
        
        Higher granularity indicates more specific, detailed content.
        Lower granularity indicates more general, overview content.
        """
        if incoming_count == 0 and outgoing_count == 0:
            return 0.5  # neutral granularity for isolated notes
        
        # Formula: balance between specificity (high incoming) and breadth (high outgoing)
        # Specific notes have many incoming links but fewer outgoing links
        # General notes have many outgoing links but fewer incoming links
        if outgoing_count == 0:
            return 1.0  # very specific
        
        ratio = incoming_count / (incoming_count + outgoing_count)
        # Normalize to 0-1 range where 1 is most granular (specific)
        return ratio
    
    def _generate_context_layers(self, note_id: str) -> Dict[str, str]:
        """
        Generate three-layer context selection strategy:
        - full: Complete note content
        - summary: AI-generated or metadata summary  
        - title: Just the note title
        """
        content = self.note_content.get(note_id, "")
        metadata = self.note_metadata.get(note_id, {})
        
        # Title layer
        title = metadata.get('title', note_id)
        
        # Summary layer (use metadata summary if available)
        summary = metadata.get('summary', None)
        if not summary and content:
            # Generate basic summary from first paragraph or first 200 chars
            first_para = content.split('\n\n')[0]
            summary = first_para[:200] + "..." if len(first_para) > 200 else first_para
        
        return {
            'title': title,
            'summary': summary or title,
            'full': content
        }
    
    def find_shortest_path(self, from_note: str, to_note: str, max_depth: int = 10) -> Optional[PathInfo]:
        """
        Find the shortest path between two notes using BFS.
        
        Args:
            from_note: Starting note ID
            to_note: Target note ID
            max_depth: Maximum search depth
            
        Returns:
            PathInfo object with path details or None if no path found
        """
        cache_key = (from_note, to_note)
        if cache_key in self._path_cache:
            return self._path_cache[cache_key]
        
        if from_note not in self.note_metadata or to_note not in self.note_metadata:
            logger.warning(f"One or both notes not found: {from_note}, {to_note}")
            return None
        
        if from_note == to_note:
            path_info = PathInfo(
                path=[from_note],
                distance=0,
                cognitive_weight=0.0,
                learning_readiness=1.0
            )
            self._path_cache[cache_key] = path_info
            return path_info
        
        # BFS to find shortest path
        queue = deque([(from_note, [from_note])])
        visited = {from_note}
        
        while queue:
            current_note, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
            
            # Get neighbors (both outgoing and incoming links)
            neighbors = self.link_graph.get(current_note, set()) | self.reverse_links.get(current_note, set())
            
            for neighbor in neighbors:
                if neighbor == to_note:
                    # Found target
                    final_path = path + [neighbor]
                    path_info = PathInfo(
                        path=final_path,
                        distance=len(final_path) - 1,
                        cognitive_weight=self._calculate_cognitive_weight(final_path),
                        learning_readiness=self._calculate_learning_readiness(from_note, to_note)
                    )
                    self._path_cache[cache_key] = path_info
                    return path_info
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        # No path found
        logger.debug(f"No path found between {from_note} and {to_note}")
        return None
    
    def _calculate_cognitive_weight(self, path: List[str]) -> float:
        """
        Calculate cognitive weight of a learning path.
        Lower weight indicates easier learning progression.
        """
        if len(path) <= 1:
            return 0.0
        
        total_weight = 0.0
        for i in range(len(path) - 1):
            current_note = path[i]
            next_note = path[i + 1]
            
            # Get complexity from metadata
            current_complexity = self.note_metadata.get(current_note, {}).get('complexity', 1)
            next_complexity = self.note_metadata.get(next_note, {}).get('complexity', 1)
            
            # Weight increases with complexity jump
            complexity_jump = abs(next_complexity - current_complexity)
            total_weight += complexity_jump
        
        # Normalize by path length
        return total_weight / (len(path) - 1)
    
    def _calculate_learning_readiness(self, from_note: str, to_note: str) -> float:
        """
        Calculate learning readiness based on the formula:
        Learning_Readiness = |prerequisites ∩ known_concepts| / |prerequisites|
        """
        # For now, use link density as a proxy for readiness
        # In a full implementation, this would analyze actual prerequisites
        
        from_analysis = self.analyze_note(from_note)
        to_analysis = self.analyze_note(to_note)
        
        if not from_analysis or not to_analysis:
            return 0.5  # neutral readiness
        
        # Higher link density of starting note indicates better foundational knowledge
        return min(from_analysis.link_density * 2, 1.0)
    
    def get_note_neighborhood(self, note_id: str, depth: int = 1) -> Dict[str, Set[str]]:
        """
        Get all notes within specified depth from the given note.
        
        Args:
            note_id: Center note ID
            depth: How many hops to include
            
        Returns:
            Dict mapping depth level to set of note IDs at that level
        """
        if note_id not in self.note_metadata:
            return {}
        
        neighborhood = {0: {note_id}}
        visited = {note_id}
        
        for current_depth in range(1, depth + 1):
            current_level = set()
            
            for note in neighborhood[current_depth - 1]:
                # Get all connected notes (bidirectional)
                connected = self.link_graph.get(note, set()) | self.reverse_links.get(note, set())
                
                for connected_note in connected:
                    if connected_note not in visited:
                        current_level.add(connected_note)
                        visited.add(connected_note)
            
            neighborhood[current_depth] = current_level
        
        return neighborhood
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the knowledge graph."""
        total_notes = len(self.note_metadata)
        total_links = sum(len(links) for links in self.link_graph.values())
        
        if total_notes == 0:
            return {
                "total_notes": 0,
                "total_links": 0,
                "avg_links_per_note": 0.0,
                "graph_density": 0.0,
                "most_connected_note": None,
                "orphaned_notes": 0
            }
        
        # Calculate averages
        avg_links = total_links / total_notes
        
        # Graph density (actual links / possible links)
        max_possible_links = total_notes * (total_notes - 1)
        density = (total_links * 2) / max_possible_links if max_possible_links > 0 else 0.0
        
        # Find most connected note
        most_connected = max(
            self.note_metadata.keys(),
            key=lambda note: len(self.link_graph.get(note, set())) + len(self.reverse_links.get(note, set())),
            default=None
        )
        
        # Count orphaned notes (no incoming or outgoing links)
        orphaned = sum(
            1 for note in self.note_metadata.keys()
            if len(self.link_graph.get(note, set())) == 0 and len(self.reverse_links.get(note, set())) == 0
        )
        
        return {
            "total_notes": total_notes,
            "total_links": total_links,
            "avg_links_per_note": avg_links,
            "graph_density": density,
            "most_connected_note": most_connected,
            "orphaned_notes": orphaned
        }
    
    def suggest_links(self, note_id: str, max_suggestions: int = 5) -> List[Tuple[str, float]]:
        """
        Suggest potential links for a note based on content similarity and graph structure.
        
        Args:
            note_id: Note to suggest links for
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of (suggested_note_id, confidence_score) tuples
        """
        if note_id not in self.note_metadata:
            return []
        
        current_outgoing = self.link_graph.get(note_id, set())
        current_incoming = self.reverse_links.get(note_id, set())
        current_connected = current_outgoing | current_incoming
        
        suggestions = []
        
        # Find notes that are connected to the same notes (collaborative filtering)
        for connected_note in current_connected:
            # Get notes connected to this connected note
            second_level = self.link_graph.get(connected_note, set()) | self.reverse_links.get(connected_note, set())
            
            for candidate in second_level:
                if candidate != note_id and candidate not in current_connected:
                    # Calculate confidence based on shared connections
                    shared_connections = len(current_connected & (
                        self.link_graph.get(candidate, set()) | self.reverse_links.get(candidate, set())
                    ))
                    confidence = shared_connections / len(current_connected) if current_connected else 0.0
                    suggestions.append((candidate, confidence))
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:max_suggestions]