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


# ── Analytics Events ──────────────────────────────────────────────────────


class AnalyticsEvent(BaseModel):
    """A single analytics event for tracking user activity."""

    id: str | None = None
    event_type: str  # "study_session", "exam_completed", "index_completed", etc.
    subject: str
    unit: str = ""
    data: dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=_utcnow)
