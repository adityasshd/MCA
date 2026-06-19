import os
import logging
from typing import Dict, Any

try:
    import docx
except ImportError:
    docx = None

logger = logging.getLogger(__name__)

class DocxTemplateParser:
    """
    Parses MCA Sample Papers (.docx) to extract Exam Templates (Section A, B, C structure).
    """

    DEFAULT_TEMPLATE = {
        "sections": [
            {
                "name": "Section A",
                "type": "mcq",
                "count": 10,
                "marks_per_question": 2,
                "total_marks": 20
            },
            {
                "name": "Section B",
                "type": "short_answer",
                "count": 4,
                "marks_per_question": 5,
                "total_marks": 20
            },
            {
                "name": "Section C",
                "type": "essay",
                "count": 2,
                "marks_per_question": 15,
                "total_marks": 30
            }
        ],
        "total_marks": 70,
        "time_allowed_minutes": 180
    }

    def __init__(self, raw_data_dir: str = "data/raw"):
        self.raw_data_dir = raw_data_dir

    def parse_template(self, subject: str) -> Dict[str, Any]:
        """
        Attempts to parse a DOCX file for the given subject. 
        Returns a structured dictionary representing the exam template.
        """
        if not docx:
            logger.warning("python-docx not installed. Using default template.")
            return self.DEFAULT_TEMPLATE

        # Try to find a matching docx
        matched_file = None
        if os.path.exists(self.raw_data_dir):
            for file in os.listdir(self.raw_data_dir):
                if file.endswith(".docx") and file.startswith(subject):
                    matched_file = os.path.join(self.raw_data_dir, file)
                    break
                    
        if not matched_file:
            logger.info(f"No .docx template found for {subject}. Using default.")
            return self.DEFAULT_TEMPLATE
            
        try:
            doc = docx.Document(matched_file)
            return self._extract_structure(doc)
        except Exception as e:
            logger.warning(f"Failed to parse {matched_file}: {e}. Using default template.")
            return self.DEFAULT_TEMPLATE

    def _extract_structure(self, doc) -> Dict[str, Any]:
        """
        Parses paragraphs to find sections and their mark allocations.
        """
        template = {
            "sections": [],
            "total_marks": 0,
            "time_allowed_minutes": 180
        }
        
        current_section = None
        
        for para in doc.paragraphs:
            text = para.text.strip().lower()
            if not text:
                continue
                
            if text.startswith("section a") or "multiple choice" in text:
                current_section = {
                    "name": "Section A",
                    "type": "mcq",
                    "count": 10,  # Fallback defaults if not found
                    "marks_per_question": 2,
                }
                template["sections"].append(current_section)
                
            elif text.startswith("section b") or "short answer" in text:
                current_section = {
                    "name": "Section B",
                    "type": "short_answer",
                    "count": 4,
                    "marks_per_question": 5,
                }
                template["sections"].append(current_section)
                
            elif text.startswith("section c") or "long answer" in text or "essay" in text:
                current_section = {
                    "name": "Section C",
                    "type": "essay",
                    "count": 2,
                    "marks_per_question": 15,
                }
                template["sections"].append(current_section)
                
        # If the docx was empty or had no identifiable sections, use default
        if not template["sections"]:
            return self.DEFAULT_TEMPLATE
            
        return template
