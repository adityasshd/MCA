"""
practice_service — Manages the Infinite Practice mode and Adaptive Mastery Engine.
"""
import logging
from datetime import datetime, timezone
from src.core.database import DatabaseManager
from src.core.schemas import PracticeSession, WeakTopic
from src.agents.study_agent import StudyAgent

logger = logging.getLogger(__name__)

class PracticeService:
    def __init__(self, db: DatabaseManager, study_agent: StudyAgent):
        self.db = db
        self.agent = study_agent

    def start_practice_session(self, subject: str, unit: str | None = None) -> PracticeSession:
        session = PracticeSession(subject=subject, unit=unit)
        session.id = self.db.practice_sessions.save(session)
        
        from src.core.schemas import AnalyticsEvent
        self.db.analytics.log(AnalyticsEvent(
            event_type="practice_started",
            subject=subject,
            unit=unit or "General"
        ))
        return session

    def update_mastery(self, subject: str, unit: str, topic: str, correct: bool) -> WeakTopic:
        weak_topic = self.db.weak_topics.get_by_topic(subject, unit, topic)
        if not weak_topic:
            weak_topic = WeakTopic(subject=subject, unit=unit, topic=topic)
        
        weak_topic.attempts += 1
        if correct:
            weak_topic.correct += 1
        else:
            weak_topic.incorrect += 1

        # Adaptive Mastery Calculation
        if weak_topic.attempts > 0:
            weak_topic.mastery_score = weak_topic.correct / weak_topic.attempts
            
        self.db.weak_topics.save(weak_topic)
        return weak_topic

    def determine_next_sequence(self, mastery_score: float) -> int:
        if mastery_score >= 0.8:
            return 0  # Move on
        elif mastery_score >= 0.6:
            return 2  # 2 Reinforcement Qs
        elif mastery_score >= 0.4:
            return 5  # 5 Reinforcement Qs
        else:
            return 8  # Mini Lesson + 8 Qs
