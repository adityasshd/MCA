"""
study_service — Orchestrates interactions between the Study Room UI, the database, and the StudyAgent.
"""
import logging
from src.core.database import DatabaseManager
from src.core.schemas import StudySession
from src.agents.study_agent import StudyAgent

logger = logging.getLogger(__name__)

class StudyService:
    def __init__(self, db: DatabaseManager, study_agent: StudyAgent):
        self.db = db
        self.agent = study_agent

    def start_session(self, subject: str, unit: str) -> str:
        session = StudySession(subject=subject, unit=unit)
        return self.db.sessions.save(session)

    def get_study_guide(self, subject: str, unit: str) -> str:
        guide = self.db.study_guides.get_by_unit(subject, unit)
        if guide:
            return guide.content
        return ""
