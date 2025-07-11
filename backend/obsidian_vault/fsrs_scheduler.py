"""
FSRS Scheduler
Implements the Free Spaced Repetition Scheduler algorithm for markdown notes
Based on Anki's FSRS algorithm for optimized review scheduling
"""

import math
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import IntEnum


logger = logging.getLogger(__name__)


class Rating(IntEnum):
    """Review rating scale"""
    AGAIN = 1     # Failed, needs immediate review
    HARD = 2      # Difficult, but remembered
    GOOD = 3      # Normal difficulty
    EASY = 4      # Too easy


class FSRSCard:
    """Represents a card/note with FSRS data"""
    
    def __init__(self, note_id: str):
        self.note_id = note_id
        self.due = datetime.now()
        self.stability = 1.0
        self.difficulty = 0.5
        self.elapsed_days = 0
        self.scheduled_days = 0
        self.reps = 0
        self.lapses = 0
        self.state = "new"  # new, learning, review, relearning
        self.last_review = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "due": self.due.isoformat(),
            "stability": self.stability,
            "difficulty": self.difficulty,
            "elapsed_days": self.elapsed_days,
            "scheduled_days": self.scheduled_days,
            "reps": self.reps,
            "lapses": self.lapses,
            "state": self.state,
            "last_review": self.last_review.isoformat() if self.last_review else None
        }
    
    @classmethod
    def from_dict(cls, note_id: str, data: Dict[str, Any]) -> "FSRSCard":
        """Create from dictionary"""
        card = cls(note_id)
        card.due = datetime.fromisoformat(data.get("due", datetime.now().isoformat()))
        card.stability = data.get("stability", 1.0)
        card.difficulty = data.get("difficulty", 0.5)
        card.elapsed_days = data.get("elapsed_days", 0)
        card.scheduled_days = data.get("scheduled_days", 0)
        card.reps = data.get("reps", 0)
        card.lapses = data.get("lapses", 0)
        card.state = data.get("state", "new")
        last_review = data.get("last_review")
        card.last_review = datetime.fromisoformat(last_review) if last_review else None
        return card


class FSRSParameters:
    """FSRS algorithm parameters"""
    
    def __init__(self):
        # Default parameters optimized for general use
        self.w = [
            0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61
        ]
        
        # Learning steps for new cards (in minutes)
        self.learning_steps = [1, 10]
        
        # Relearning steps for failed cards (in minutes)
        self.relearning_steps = [10]
        
        # Graduating interval (days)
        self.graduating_interval = 1
        
        # Easy interval (days)
        self.easy_interval = 4
        
        # Maximum interval (days)
        self.maximum_interval = 36500  # 100 years
        
        # Hard interval multiplier
        self.hard_multiplier = 1.2
        
        # Easy bonus
        self.easy_bonus = 1.3


class FSRSScheduler:
    """Free Spaced Repetition Scheduler for markdown notes"""
    
    def __init__(self, parameters: FSRSParameters = None):
        self.params = parameters or FSRSParameters()
        self.cards: Dict[str, FSRSCard] = {}
        self.review_log: List[Dict[str, Any]] = []
    
    async def initialize_note_fsrs(self, note_id: str = None) -> Dict[str, Any]:
        """Initialize FSRS data for a new note"""
        fsrs_data = {
            "due": (datetime.now() + timedelta(days=1)).isoformat(),
            "stability": 1.0,
            "difficulty": 0.5,
            "elapsed_days": 0,
            "scheduled_days": 0,
            "reps": 0,
            "lapses": 0,
            "state": "new",
            "last_review": None
        }
        
        if note_id:
            self.cards[note_id] = FSRSCard.from_dict(note_id, fsrs_data)
        
        return fsrs_data
    
    async def review_card(self, note_id: str, rating: Rating) -> Dict[str, Any]:
        """Process a review and update card scheduling"""
        
        if note_id not in self.cards:
            # Initialize card if it doesn't exist
            await self.initialize_note_fsrs(note_id)
        
        card = self.cards[note_id]
        now = datetime.now()
        
        # Calculate elapsed days since last review
        if card.last_review:
            card.elapsed_days = (now - card.last_review).days
        else:
            card.elapsed_days = 0
        
        # Update card based on rating
        if card.state == "new":
            card = await self._review_new_card(card, rating)
        elif card.state == "learning":
            card = await self._review_learning_card(card, rating)
        elif card.state == "review":
            card = await self._review_review_card(card, rating)
        elif card.state == "relearning":
            card = await self._review_relearning_card(card, rating)
        
        # Update review count and last review time
        card.reps += 1
        card.last_review = now
        
        # Log the review
        self.review_log.append({
            "note_id": note_id,
            "rating": rating,
            "timestamp": now.isoformat(),
            "old_due": card.due.isoformat(),
            "new_due": card.due.isoformat(),
            "stability": card.stability,
            "difficulty": card.difficulty
        })
        
        logger.info(f"Reviewed note {note_id}: rating={rating}, next_due={card.due}")
        
        return card.to_dict()
    
    async def _review_new_card(self, card: FSRSCard, rating: Rating) -> FSRSCard:
        """Handle review of new card"""
        
        if rating == Rating.AGAIN:
            # Card failed, goes to learning
            card.state = "learning"
            card.due = datetime.now() + timedelta(minutes=self.params.learning_steps[0])
            card.scheduled_days = 0
        elif rating in [Rating.HARD, Rating.GOOD]:
            # Card passed, but goes through learning steps
            card.state = "learning"
            if len(self.params.learning_steps) > 1:
                card.due = datetime.now() + timedelta(minutes=self.params.learning_steps[1])
            else:
                card.due = datetime.now() + timedelta(days=self.params.graduating_interval)
        elif rating == Rating.EASY:
            # Card is easy, skip learning and go straight to review
            card.state = "review"
            card.stability = self.params.easy_interval
            card.due = datetime.now() + timedelta(days=self.params.easy_interval)
            card.scheduled_days = self.params.easy_interval
        
        return card
    
    async def _review_learning_card(self, card: FSRSCard, rating: Rating) -> FSRSCard:
        """Handle review of learning card"""
        
        if rating == Rating.AGAIN:
            # Restart learning
            card.due = datetime.now() + timedelta(minutes=self.params.learning_steps[0])
            card.lapses += 1
        elif rating in [Rating.HARD, Rating.GOOD, Rating.EASY]:
            # Graduate to review state
            card.state = "review"
            
            if rating == Rating.EASY:
                interval = self.params.easy_interval
            else:
                interval = self.params.graduating_interval
            
            card.stability = interval
            card.due = datetime.now() + timedelta(days=interval)
            card.scheduled_days = interval
        
        return card
    
    async def _review_review_card(self, card: FSRSCard, rating: Rating) -> FSRSCard:
        """Handle review of review card using FSRS algorithm"""
        
        if rating == Rating.AGAIN:
            # Card failed, goes to relearning
            card.state = "relearning"
            card.due = datetime.now() + timedelta(minutes=self.params.relearning_steps[0])
            card.lapses += 1
            card.difficulty = min(card.difficulty + 0.2, 1.0)
        else:
            # Update stability and difficulty using FSRS formulas
            retrievability = self._calculate_retrievability(card)
            
            if rating == Rating.HARD:
                card.difficulty = max(card.difficulty - 0.15, 0.0)
                new_stability = card.stability * self.params.hard_multiplier
            elif rating == Rating.GOOD:
                card.difficulty = max(card.difficulty - 0.1, 0.0)
                new_stability = self._calculate_new_stability(card, retrievability, rating)
            elif rating == Rating.EASY:
                card.difficulty = max(card.difficulty - 0.05, 0.0)
                new_stability = self._calculate_new_stability(card, retrievability, rating) * self.params.easy_bonus
            
            card.stability = min(new_stability, self.params.maximum_interval)
            
            # Calculate next review date
            interval = max(1, int(card.stability))
            card.due = datetime.now() + timedelta(days=interval)
            card.scheduled_days = interval
        
        return card
    
    async def _review_relearning_card(self, card: FSRSCard, rating: Rating) -> FSRSCard:
        """Handle review of relearning card"""
        
        if rating == Rating.AGAIN:
            # Stay in relearning
            card.due = datetime.now() + timedelta(minutes=self.params.relearning_steps[0])
        else:
            # Graduate back to review
            card.state = "review"
            interval = max(1, int(card.stability))
            card.due = datetime.now() + timedelta(days=interval)
            card.scheduled_days = interval
        
        return card
    
    def _calculate_retrievability(self, card: FSRSCard) -> float:
        """Calculate current retrievability of the card"""
        if card.stability <= 0:
            return 0.0
        
        return math.pow(1 + card.elapsed_days / (9 * card.stability), -1)
    
    def _calculate_new_stability(self, card: FSRSCard, retrievability: float, rating: Rating) -> float:
        """Calculate new stability using FSRS formula"""
        
        # Simplified FSRS formula
        if rating == Rating.HARD:
            factor = self.params.w[15] * (1 - retrievability)
        elif rating == Rating.GOOD:
            factor = self.params.w[8] + (card.elapsed_days / card.stability - 1) * self.params.w[9]
        elif rating == Rating.EASY:
            factor = self.params.w[10] * (2 - retrievability)
        else:
            factor = 1.0
        
        return max(card.stability * factor, 0.1)
    
    async def get_due_cards(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get cards that are due for review"""
        
        now = datetime.now()
        due_cards = []
        
        for note_id, card in self.cards.items():
            if card.due <= now:
                due_cards.append({
                    "note_id": note_id,
                    "due": card.due,
                    "state": card.state,
                    "stability": card.stability,
                    "difficulty": card.difficulty,
                    "overdue_days": (now - card.due).days
                })
        
        # Sort by due date (most overdue first)
        due_cards.sort(key=lambda x: x["due"])
        
        return due_cards[:limit]
    
    async def generate_review_question(self, note_id: str, note_content: str) -> Dict[str, Any]:
        """Generate a review question for a note"""
        
        card = self.cards.get(note_id)
        if not card:
            return {"error": "Card not found"}
        
        # Extract key concepts from note content
        key_concepts = self._extract_key_concepts(note_content)
        
        # Generate question based on difficulty and content
        if card.difficulty < 0.3:
            # Easy questions
            question_type = "recognition"
            question = f"Which of these concepts is related to the main topic?"
        elif card.difficulty < 0.7:
            # Medium questions
            question_type = "recall"
            question = f"Can you explain the main concept in your own words?"
        else:
            # Hard questions
            question_type = "application"
            question = f"How would you apply this concept in a real-world scenario?"
        
        return {
            "note_id": note_id,
            "question": question,
            "question_type": question_type,
            "key_concepts": key_concepts,
            "difficulty": card.difficulty,
            "stability": card.stability
        }
    
    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts from note content"""
        
        # Simple extraction - in practice, use NLP
        import re
        
        # Find words in [[double brackets]]
        links = re.findall(r'\[\[([^\]]+)\]\]', content)
        
        # Find headings
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        # Find bolded terms
        bold_terms = re.findall(r'\*\*([^*]+)\*\*', content)
        
        key_concepts = list(set(links + headings + bold_terms))
        
        return key_concepts[:5]  # Return top 5
    
    async def update_parameters(self, optimization_data: List[Dict[str, Any]]):
        """Update FSRS parameters based on review history"""
        
        # This would implement parameter optimization
        # For now, we'll use default parameters
        logger.info("Parameter optimization not yet implemented, using defaults")
    
    async def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        
        now = datetime.now()
        
        total_cards = len(self.cards)
        due_count = len([c for c in self.cards.values() if c.due <= now])
        new_count = len([c for c in self.cards.values() if c.state == "new"])
        learning_count = len([c for c in self.cards.values() if c.state in ["learning", "relearning"]])
        review_count = len([c for c in self.cards.values() if c.state == "review"])
        
        # Average difficulty and stability
        if total_cards > 0:
            avg_difficulty = sum(c.difficulty for c in self.cards.values()) / total_cards
            avg_stability = sum(c.stability for c in self.cards.values()) / total_cards
        else:
            avg_difficulty = avg_stability = 0
        
        # Review activity (last 7 days)
        week_ago = now - timedelta(days=7)
        recent_reviews = [
            r for r in self.review_log 
            if datetime.fromisoformat(r["timestamp"]) >= week_ago
        ]
        
        return {
            "total_cards": total_cards,
            "due_count": due_count,
            "new_count": new_count,
            "learning_count": learning_count,
            "review_count": review_count,
            "average_difficulty": avg_difficulty,
            "average_stability": avg_stability,
            "reviews_last_7_days": len(recent_reviews),
            "total_reviews": len(self.review_log)
        }
    
    async def predict_workload(self, days_ahead: int = 7) -> Dict[str, List[int]]:
        """Predict review workload for upcoming days"""
        
        workload = {}
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(days_ahead):
            target_date = today + timedelta(days=i)
            end_date = target_date + timedelta(days=1)
            
            due_on_date = len([
                c for c in self.cards.values() 
                if target_date <= c.due < end_date
            ])
            
            workload[target_date.strftime("%Y-%m-%d")] = due_on_date
        
        return {
            "daily_workload": workload,
            "peak_day": max(workload.items(), key=lambda x: x[1]) if workload else None,
            "total_upcoming": sum(workload.values())
        }"