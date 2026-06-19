"""
exam_template_parser — Parses DOCX sample papers to extract structural constraints for the University Exam Simulator.
"""
import logging
import re
from pathlib import Path
import docx

logger = logging.getLogger(__name__)

class ExamTemplateParser:
    """
    Parses a DOCX file to infer examination structure (e.g., Section A/B/C, marks distribution, question patterns).
    """
    def __init__(self):
        # Common patterns for marks e.g. [5 marks], (10), etc.
        self.marks_pattern = re.compile(r'\[?\(?(\d+(?:\.\d+)?)\s*(?:marks?|m)\)?\]?', re.IGNORECASE)
        # Common pattern for sections e.g. SECTION A, Part 1
        self.section_pattern = re.compile(r'^(?:SECTION|PART)\s+([A-Z0-9]+)', re.IGNORECASE)

    def parse(self, file_path: str) -> dict:
        """
        Extracts structural constraints from the document.
        Returns a dictionary representing the template structure.
        """
        path = Path(file_path)
        if not path.exists() or path.suffix.lower() != ".docx":
            raise ValueError(f"Invalid DOCX file path: {file_path}")

        doc = docx.Document(file_path)
        
        structure = {
            "filename": path.name,
            "sections": [],
            "total_marks": 0,
            "estimated_questions": 0
        }
        
        current_section = None

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Check for section headers
            sec_match = self.section_pattern.search(text)
            if sec_match or text.isupper():
                if current_section:
                    structure["sections"].append(current_section)
                
                sec_name = text if text.isupper() else sec_match.group(0)
                current_section = {
                    "name": sec_name,
                    "questions": [],
                    "total_section_marks": 0
                }
                continue

            # If no section defined yet, create a default 'General' section
            if not current_section:
                current_section = {
                    "name": "General",
                    "questions": [],
                    "total_section_marks": 0
                }

            # Check for marks to identify a question
            marks_match = self.marks_pattern.search(text)
            marks = float(marks_match.group(1)) if marks_match else 0.0
            
            if marks > 0 or re.match(r'^(Q\d+|\d+\.)', text):
                current_section["questions"].append({
                    "text": text,
                    "marks": marks
                })
                current_section["total_section_marks"] += marks
                structure["estimated_questions"] += 1
                structure["total_marks"] += marks

        # Append last section
        if current_section and current_section["questions"]:
            structure["sections"].append(current_section)

        return structure

    def generate_prompt_constraints(self, structure: dict) -> str:
        """
        Converts the parsed structure into an LLM instruction block.
        """
        instructions = f"Generate an exam matching the exact structure of {structure['filename']}:\n"
        instructions += f"Total Marks: {structure['total_marks']}\n\n"
        
        for sec in structure["sections"]:
            instructions += f"--- {sec['name']} ---\n"
            instructions += f"Section Marks: {sec['total_section_marks']}\n"
            instructions += f"Generate {len(sec['questions'])} questions following this pattern:\n"
            for q in sec['questions']:
                instructions += f"- Pattern: {q['text'][:50]}... (Marks: {q['marks']})\n"
            instructions += "\n"
            
        return instructions
