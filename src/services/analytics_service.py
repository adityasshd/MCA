"""
analytics_service — Provides data for the Knowledge Mastery Map and Plotly charts.
"""
import logging
from src.core.database import DatabaseManager

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_knowledge_mastery_map(self) -> dict:
        """Returns hierarchical dictionary of mastery scores."""
        topics = self.db.weak_topics.get_weakest(limit=1000)
        mastery_map = {}
        for t in topics:
            if t.subject not in mastery_map:
                mastery_map[t.subject] = {}
            if t.topic not in mastery_map[t.subject]:
                mastery_map[t.subject][t.topic] = t.mastery_score
        return mastery_map
