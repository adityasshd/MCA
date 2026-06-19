"""
template_service — Manages DOCX template parsing and caching.
"""
import logging
from src.core.database import DatabaseManager
from src.core.schemas import ExamTemplate
from src.core.exam_template_parser import ExamTemplateParser

logger = logging.getLogger(__name__)

class TemplateService:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.parser = ExamTemplateParser()

    def parse_and_cache(self, file_path: str) -> ExamTemplate:
        """Parses a DOCX template and caches its structure in the database."""
        structure = self.parser.parse(file_path)
        
        # We need a subject mapping logic, but for now we fallback to filename
        subject = "Unknown" 
        
        template = ExamTemplate(
            subject=subject,
            filename=structure["filename"],
            structure=structure
        )
        self.db.exam_templates.save(template)
        return template

    def get_template(self, filename: str) -> ExamTemplate | None:
        return self.db.exam_templates.get_by_filename(filename)

    def get_all_by_subject(self, subject: str) -> list[ExamTemplate]:
        return self.db.exam_templates.get_by_subject(subject)
