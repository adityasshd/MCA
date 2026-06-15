"""
workers — PyQt6 QThread Background Tasks
==========================================
Wraps long-running tasks (LLM calls, DB queries, RAG indexing) into
QObject workers moved to QThreads to keep the UI responsive.
"""

from PyQt6.QtCore import QObject, pyqtSignal

from src.agents.examiner_agent import ExaminerAgent
from src.agents.study_agent import StudyAgent
from src.core.database import DatabaseManager
from src.core.models import BaseEmbedder, ModelManager
from src.core.schemas import Exam, QuestionType, StudySession
from src.rag.indexer import index_subject


# ── RAG Indexing ────────────────────────────────────────────────────────


class IndexWorker(QObject):
    progress = pyqtSignal(str)          # emit progress messages
    finished = pyqtSignal(int)          # emit total chunks generated
    error = pyqtSignal(str)

    def __init__(
        self,
        db: DatabaseManager,
        embedder: BaseEmbedder,
        subject_name: str,
        force_reindex: bool = False,
    ):
        super().__init__()
        self.db = db
        self.embedder = embedder
        self.subject_name = subject_name
        self.force_reindex = force_reindex

    def run(self):
        try:
            def on_progress(msg: str):
                self.progress.emit(msg)
                
            total_chunks = index_subject(
                self.subject_name,
                self.embedder,
                self.db,
                progress_callback=on_progress,
                force_reindex=self.force_reindex,
            )
            self.finished.emit(total_chunks)
        except Exception as e:
            self.error.emit(str(e))


# ── Study Chat & Guides ──────────────────────────────────────────────────

class StudyGuideWorker(QObject):
    chunk = pyqtSignal(str)      # Emit streaming markdown chunks
    done = pyqtSignal()          # Emit when generation is fully complete
    error = pyqtSignal(str)

    def __init__(self, agent: StudyAgent, subject: str, unit: str):
        super().__init__()
        self.agent = agent
        self.subject = subject
        self.unit = unit
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            full_text = ""
            for text_chunk in self.agent.generate_study_guide(self.subject, self.unit):
                if getattr(self, '_is_cancelled', False):
                    break
                full_text += text_chunk
                try:
                    self.chunk.emit(text_chunk)
                except RuntimeError:
                    break
                
            # Save to DB cache for future fast-retrieval
            if not getattr(self, '_is_cancelled', False):
                self.agent.save_study_guide(self.subject, self.unit, full_text)
                try:
                    self.done.emit()
                except RuntimeError:
                    pass
        except Exception as e:
            try:
                self.error.emit(str(e))
            except RuntimeError:
                pass

class ChatWorker(QObject):
    chunk = pyqtSignal(str)      # Emit streaming text chunks
    done = pyqtSignal(str)       # Emit full response text
    error = pyqtSignal(str)

    def __init__(self, agent: StudyAgent, session: StudySession, message: str):
        super().__init__()
        self.agent = agent
        self.session = session
        self.message = message

    def run(self):
        try:
            full_text = ""
            for text_chunk in self.agent.chat(self.session, self.message):
                full_text += text_chunk
                self.chunk.emit(text_chunk)
            self.done.emit(full_text)
        except Exception as e:
            self.error.emit(str(e))


# ── Exam Generation & Grading ─────────────────────────────────────────


class ExamGenWorker(QObject):
    finished = pyqtSignal(Exam)
    error = pyqtSignal(str)

    def __init__(
        self,
        agent: ExaminerAgent,
        subject: str,
        scope: str,
        types: list[QuestionType],
        count: int,
    ):
        super().__init__()
        self.agent = agent
        self.subject = subject
        self.scope = scope
        self.types = types
        self.count = count

    def run(self):
        try:
            exam = self.agent.generate_exam(
                self.subject, self.scope, self.types, self.count
            )
            self.finished.emit(exam)
        except Exception as e:
            self.error.emit(str(e))


class GradeWorker(QObject):
    finished = pyqtSignal(float)  # emit overall score
    error = pyqtSignal(str)

    def __init__(self, agent: ExaminerAgent, exam: Exam):
        super().__init__()
        self.agent = agent
        self.exam = exam

    def run(self):
        try:
            score = self.agent.grade_exam(self.exam)
            self.finished.emit(score)
        except Exception as e:
            self.error.emit(str(e))


# ── Analytics Reporting ────────────────────────────────────────────────


class ReportWorker(QObject):
    finished = pyqtSignal(dict)  # emits a dict of Matplotlib Figures
    error = pyqtSignal(str)

    def __init__(self, builder, subject: str | None = None):
        super().__init__()
        self.builder = builder
        self.subject = subject

    def run(self):
        try:
            figs = {
                "trends": self.builder.plot_score_trends(self.subject),
                "heatmap": self.builder.plot_topic_heatmap(self.subject),
                "types": self.builder.plot_question_types(self.subject),
            }
            self.finished.emit(figs)
        except Exception as e:
            self.error.emit(str(e))
