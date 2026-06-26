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

    def get_practice_question(self, subject: str, unit: str, topic: str | None = None, difficulty: str = "Medium", exclude_ids: list[str] = None) -> dict:
        """
        Retrieves a practice question, preferring the local question bank.
        If empty, it generates one on the fly and caches it.
        """
        # Check cache
        topic_val = topic or ""
        q_item = self.db.question_bank.get_question(subject, unit, topic_val, difficulty, exclude_ids)
        
        if q_item:
            # Update usage stats
            q_item.times_served += 1
            self.db.question_bank.update(q_item)
            
            # Stock background if getting low
            count = self.db.question_bank.count_by_topic(subject, unit, topic_val)
            if count < 5:
                self.stock_questions_background(subject, unit, topic_val, difficulty)
                
            return {
                "id": q_item.id,
                "question": q_item.prompt,
                "options": q_item.options,
                "answer": q_item.expected_answer,
                "explanation": q_item.explanation
            }
            
        # Fallback: Generate one on the fly
        logger.info(f"Question bank empty for {subject}-{unit}-{topic_val}. Generating on the fly...")
        q_data = self.agent.generate_practice_question(subject, unit, topic_val, difficulty)
        
        # Save to DB if valid
        if "Error generating" not in q_data.get("question", ""):
            from src.core.schemas import QuestionBankItem, QuestionType
            new_item = QuestionBankItem(
                subject=subject,
                unit=unit,
                topic=topic_val,
                difficulty=difficulty,
                question_type=QuestionType.MCQ,
                prompt=q_data["question"],
                options=q_data["options"],
                expected_answer=q_data["answer"],
                explanation=q_data.get("explanation"),
                times_served=1
            )
            q_id = self.db.question_bank.save(new_item)
            q_data["id"] = q_id
            
        return q_data

    def stock_questions_background(self, subject: str, unit: str, topic: str, difficulty: str) -> None:
        """
        Spawns a daemon thread to generate a batch of questions for the bank.
        """
        import threading
        
        def worker():
            logger.info(f"Background stocking started for {subject}-{unit}-{topic}")
            for _ in range(5):
                q_data = self.agent.generate_practice_question(subject, unit, topic, difficulty)
                if "Error generating" not in q_data.get("question", ""):
                    from src.core.schemas import QuestionBankItem, QuestionType
                    new_item = QuestionBankItem(
                        subject=subject,
                        unit=unit,
                        topic=topic,
                        difficulty=difficulty,
                        question_type=QuestionType.MCQ,
                        prompt=q_data["question"],
                        options=q_data["options"],
                        expected_answer=q_data["answer"],
                        explanation=q_data.get("explanation")
                    )
                    self.db.question_bank.save(new_item)
            logger.info(f"Background stocking finished for {subject}-{unit}-{topic}")
            
        t = threading.Thread(target=worker, daemon=True)
        t.start()
