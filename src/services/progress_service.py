"""
progress_service — Manages the Learning Journey (Subject, Unit, Topic progress, and Revision scheduling).
"""
import logging
from src.core.database import DatabaseManager
from src.core.schemas import StudyProgress

logger = logging.getLogger(__name__)

class ProgressService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_progress(self, subject: str, unit: str) -> StudyProgress:
        p = self.db.progress.get_by_unit(subject, unit)
        if not p:
            p = StudyProgress(subject=subject, unit=unit)
            p.id = self.db.progress.save(p)
        return p
