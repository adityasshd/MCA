"""
examiner_agent — Test Generation and Grading
==============================================
Uses the reasoning model (Tier 2) to generate ad-hoc exams based on
the syllabus and retrieved content. Implements a two-pass grading system.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from src.core.database import DatabaseManager
from src.core.models import ModelManager
from src.core.schemas import Exam, ExamQuestion, QuestionType
from src.rag.retriever import Retriever

logger = logging.getLogger(__name__)


from src.core.prompt_manager import PromptManager


class ExaminerAgent:
    def __init__(
        self,
        db: DatabaseManager,
        model_manager: ModelManager,
        retriever: Retriever,
    ) -> None:
        self.db = db
        self.model_manager = model_manager
        self.retriever = retriever
        self.prompt_manager = PromptManager()

    def generate_exam(
        self,
        subject: str,
        scope: str,  # unit name or "All"
        types: list[QuestionType],
        count: int = 5,
        mode: str = "custom",
    ) -> Exam:
        """
        Generate a new exam using the reasoning model.
        """
        # Distribute types
        if mode == "official":
            from src.rag.docx_parser import DocxTemplateParser
            parser = DocxTemplateParser()
            template = parser.parse_template(subject)
            total_questions = sum(sec.get("count", 0) for sec in template["sections"])
            count = total_questions
            type_str = ", ".join(sec.get("type", "") for sec in template["sections"])
            
            sec_instructions = []
            for sec in template["sections"]:
                sec_instructions.append(f"- {sec['name']}: {sec['count']} questions of type '{sec['type']}'")
            structure_context = "Generate the exam exactly matching this structure:\n" + "\n".join(sec_instructions)
        else:
            type_str = ", ".join(t.value for t in types)
            structure_context = ""

        unit_filter = scope if scope != "All" else None
        chunks = self.retriever.retrieve(
            query=f"Core concepts and definitions for {scope}",
            subject=subject,
            unit=unit_filter,
            top_k=10,
        )
        context = self.retriever.format_context(chunks)

        prompt = self.prompt_manager.get_prompt(
            "examiner_exam_gen",
            subject=subject,
            scope=scope,
            count=count,
            types_distribution=type_str,
            context=context,
        )
        if mode == "official":
            prompt += f"\n\nIMPORTANT OFFICIAL EXAM CONSTRAINTS:\n{structure_context}\nEnsure your JSON output produces exactly {count} questions following these section counts and types."


        llm = self.model_manager.thinking

        try:
            response_text = llm.generate(
                prompt=prompt,
                system="You are an expert exam generator. Output only JSON.",
                temperature=0.4,
            )
            
            # Clean up potential markdown formatting around JSON
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            parsed = json.loads(response_text.strip())

            questions = []
            for q_data in parsed:
                q = ExamQuestion(
                    type=QuestionType(q_data["type"]),
                    prompt=q_data["prompt"],
                    options=q_data.get("options"),
                    expected_answer=q_data["expected_answer"],
                )
                questions.append(q)

            exam = Exam(
                subject=subject,
                scope=scope,
                questions=questions,
            )
            
            # Save the exam without scores initially
            exam_id = self.db.exams.save(exam)
            exam.id = exam_id
            
            return exam

        except Exception as e:
            logger.error("Failed to generate exam: %s", e)
            raise

    def grade_exam(self, exam: Exam) -> float:
        """
        Grade an exam using the two-pass system.
        Updates the exam object in place and saves to the database.
        Returns the overall score (0.0 to 1.0).
        """
        fast_llm = self.model_manager.fast
        thinking_llm = self.model_manager.thinking
        
        total_score = 0.0

        for q in exam.questions:
            # If the student didn't answer, grade is 0
            if not q.user_answer.strip():
                q.grade = 0.0
                q.feedback = "No answer provided."
                continue

            if q.type in (QuestionType.MCQ, QuestionType.TRUE_FALSE, QuestionType.FILL_IN_BLANK):
                # Pass 1: Instant Fast Grading
                ua = q.user_answer.strip().lower()
                ea = q.expected_answer.strip().lower()
                
                is_correct = False
                if q.type in (QuestionType.MCQ, QuestionType.TRUE_FALSE):
                    is_correct = (ua == ea)
                else:
                    is_correct = (ea in ua) or (ua == ea)
                    
                q.grade = 1.0 if is_correct else 0.0
                if is_correct:
                    q.feedback = "Correct! Well done."
                else:
                    q.feedback = f"Incorrect. The correct answer is:\n\n{q.expected_answer}"

            else:
                # Pass 2: Detailed grading for essays
                prompt = self.prompt_manager.get_prompt(
                    "examiner_pass_2",
                    prompt=q.prompt,
                    expected=q.expected_answer,
                    student=q.user_answer,
                )
                
                try:
                    res = thinking_llm.generate(
                        prompt, 
                        system="Output only JSON.", 
                        temperature=0.2
                    )
                    res = self._clean_json(res)
                    data = json.loads(res)
                    q.grade = float(data.get("grade", 0.0))
                    q.feedback = data.get("feedback", "")
                except Exception as e:
                    logger.warning("Detailed grading failed: %s", e)
                    q.grade = 0.0
                    q.feedback = f"Automated grading failed: {e}"
            
            # Bound grade
            if q.grade is not None:
                q.grade = max(0.0, min(1.0, q.grade))
                total_score += q.grade

        if exam.questions:
            exam.score = total_score / len(exam.questions)
        else:
            exam.score = 0.0

        # Note: We need a way to update the exam in the DB
        # For now, we assume the DB handles upserts on save() if ID is set
        self.db.exams.save(exam)
        
        # Log analytics
        from src.core.schemas import AnalyticsEvent
        self.db.analytics.log(AnalyticsEvent(
            event_type="exam_completed",
            subject=exam.subject,
            unit=exam.scope,
            data={"score": exam.score, "num_questions": len(exam.questions)}
        ))

        return exam.score

    def _clean_json(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
