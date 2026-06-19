"""
schemas — Pydantic Domain Models (Transition Layer)
====================================================
All data flows through these models regardless of which database backend
is active. They serve as the contract between business logic and storage.

Every repository backend serializes from / deserializes to these schemas
using Pydantic's model_dump() / model_validate().
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


# ── Subject & Indexing ─────────────────────────────────────────────────────


class UnitInfo(BaseModel):
    """Metadata for a single unit/chapter within a subject."""

    name: str
    file_path: str
    indexed: bool = False
    chunk_count: int = 0


class Subject(BaseModel):
    """A subject (course book) containing multiple units/chapters."""

    id: str | None = None
    name: str
    folder_path: str
    units: list[UnitInfo] = []
    created_at: datetime = Field(default_factory=_utcnow)


# ── RAG Text Chunks ───────────────────────────────────────────────────────


class TextChunk(BaseModel):
    """
    A single text chunk from a chapter PDF, stored alongside its embedding
    vector in MongoDB Atlas for vector search.
    """

    id: str | None = None
    subject: str
    unit: str
    chunk_index: int
    text: str
    page_range: str = ""  # e.g., "3-5"
    embedding: list[float] = []
    embedding_model: str = ""  # tracks which model created this embedding


class RetrievedChunk(BaseModel):
    """A chunk returned from a search query, with a relevance score."""

    text: str
    subject: str
    unit: str
    chunk_index: int
    page_range: str = ""
    score: float = 0.0


# ── Study Sessions ────────────────────────────────────────────────────────


class ChatMessage(BaseModel):
    """A single message in a study chat session."""

    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: datetime = Field(default_factory=_utcnow)


class StudySession(BaseModel):
    """A complete study chat session for a subject/unit."""

    id: str | None = None
    subject: str
    unit: str
    messages: list[ChatMessage] = []
    started_at: datetime = Field(default_factory=_utcnow)
    ended_at: datetime | None = None


# ── Study Guides ──────────────────────────────────────────────────────────


class StudyGuide(BaseModel):
    """A generated markdown study guide for a unit, cached to save API calls."""

    id: str | None = None
    subject: str
    unit: str
    content: str
    created_at: datetime = Field(default_factory=_utcnow)


# ── Exams ─────────────────────────────────────────────────────────────────


class QuestionType(str, Enum):
    """Types of exam questions the system can generate."""

    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"
    FILL_IN_BLANK = "fill_in_blank"


class ExamQuestion(BaseModel):
    """A single exam question with grading information."""

    type: QuestionType
    prompt: str
    options: list[str] | None = None  # MCQ only
    expected_answer: str = ""
    user_answer: str = ""
    grade: float | None = None  # 0.0 – 1.0
    feedback: str = ""


class Exam(BaseModel):
    """A complete exam session with questions and scores."""

    id: str | None = None
    subject: str
    scope: str  # unit name, "chapter", or "full_book"
    questions: list[ExamQuestion] = []
    score: float | None = None
    created_at: datetime = Field(default_factory=_utcnow)


class ExamSession(BaseModel):
    """Centralized state object for an active exam."""

    exam_id: str | None = None
    subject: str
    scope: str
    questions: list[ExamQuestion] = []
    answers: dict[int, str] = {}  # Map of question index to user answer
    current_question_index: int = 0
    flagged_questions: list[int] = []
    started_at: datetime = Field(default_factory=_utcnow)
    mode: str = "standard"  # "standard" or "focus"
    score: float | None = None


# ── Analytics Events ──────────────────────────────────────────────────────


class AnalyticsEvent(BaseModel):
    """A single analytics event for tracking user activity."""

    id: str | None = None
    event_type: str  # "study_session", "exam_completed", "index_completed", etc.
    subject: str
    unit: str = ""
    data: dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=_utcnow)


# ── Adaptive Learning & Persistence ────────────────────────────────────────

class UserStats(BaseModel):
    """Overall user statistics and global progress metrics."""

    id: str | None = None
    current_streak: int = 0
    total_study_hours: float = 0.0
    weekly_goal_hours: float = 5.0
    last_active: datetime = Field(default_factory=_utcnow)
    topic_stats: dict[str, dict[str, float | int]] = {}  # "topic": {"attempts": int, "incorrect": int, "correct": int, "mastery_score": float}


class StudyProgress(BaseModel):
    """Tracks progression and revision schedules for subjects/units."""

    id: str | None = None
    subject: str
    unit: str
    last_practiced: datetime | None = None
    revision_due_date: datetime | None = None
    confidence_score: float = 0.0


class WeakTopic(BaseModel):
    """Tracks mastery score and failure rates for specific topics."""

    id: str | None = None
    subject: str
    unit: str
    topic: str
    attempts: int = 0
    correct: int = 0
    incorrect: int = 0
    mastery_score: float = 0.0


class PracticeSession(BaseModel):
    """Tracks an infinite practice flow sequence and outcomes."""

    id: str | None = None
    subject: str
    unit: str | None = None
    questions_answered: int = 0
    correct_answers: int = 0
    started_at: datetime = Field(default_factory=_utcnow)
    ended_at: datetime | None = None


class ExamHistory(BaseModel):
    """Detailed logs of past exams for prediction modeling and history."""

    id: str | None = None
    exam_id: str
    subject: str
    score: float
    topic_breakdown: dict[str, float] = {}  # e.g. {"Binary Conversion": 0.8}
    taken_at: datetime = Field(default_factory=_utcnow)


class ExamTemplate(BaseModel):
    """Cached structural constraints parsed from DOCX templates."""

    id: str | None = None
    subject: str
    filename: str
    structure: dict[str, Any] = {}  # Details about Section A/B/C, marks, etc.
    parsed_at: datetime = Field(default_factory=_utcnow)


class QuestionBankItem(BaseModel):
    """A persistently cached question for reuse and offline mode."""

    id: str | None = None
    subject: str
    unit: str
    topic: str
    difficulty: str
    question_type: QuestionType = QuestionType.MCQ
    prompt: str
    options: list[str] | None = None
    expected_answer: str
    explanation: str | None = None
    times_served: int = 0
    times_correct: int = 0
    times_incorrect: int = 0
    avg_response_time: float = 0.0
    created_at: datetime = Field(default_factory=_utcnow)


class ModelAssignment(BaseModel):
    """Stores the provider and model name assigned to a specific AI task."""
    
    provider: str
    model: str


class AppSettings(BaseModel):
    """Global user settings, API keys, and model configurations, stored in DB."""

    id: str | None = "global"
    api_keys: dict[str, str] = {
        "groq": "",
        "openai": "",
        "gemini": "",
        "openrouter": "",
        "kaggle": "",
        "mongodb": ""
    }
    task_models: dict[str, ModelAssignment] = {
        "tutor": ModelAssignment(provider="ollama", model="llama3.2:1b"),
        "practice": ModelAssignment(provider="ollama", model="llama3.2:1b"),
        "exam": ModelAssignment(provider="ollama", model="qwen2.5:1.5b"),
        "study_guide": ModelAssignment(provider="ollama", model="qwen2.5:1.5b"),
        "analytics": ModelAssignment(provider="ollama", model="qwen2.5:1.5b")
    }

