"""
database — Repository Pattern with Swappable Backends
======================================================
Defines Protocol-based repository contracts and concrete implementations.
All data passes through Pydantic schemas (src/core/schemas.py) at the
boundary — backends serialize/deserialize via model_dump() / model_validate().

Architecture:
    UI / Agent  →  Pydantic Model  →  Repository Protocol  →  Backend
                   (schemas.py)       (this file)              ├─ MongoRepo (Atlas)
                                                               ├─ SQLiteRepo (local)
                                                               └─ MemoryRepo (testing)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Protocol

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.operations import SearchIndexModel

from src.core.schemas import (
    AnalyticsEvent,
    Exam,
    RetrievedChunk,
    StudySession,
    StudyGuide,
    Subject,
    TextChunk,
    UserStats,
    StudyProgress,
    WeakTopic,
    PracticeSession,
    ExamHistory,
    ExamTemplate,
    AppSettings,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
#  Repository Protocols (Contracts)
# ═══════════════════════════════════════════════════════════════════════════


class SubjectRepository(Protocol):
    """Contract for subject CRUD operations."""

    def save(self, subject: Subject) -> str: ...
    def get_by_name(self, name: str) -> Subject | None: ...
    def get_all(self) -> list[Subject]: ...
    def update(self, subject: Subject) -> None: ...
    def delete(self, subject_id: str) -> None: ...


class ChunkRepository(Protocol):
    """Contract for text chunk storage and vector search."""

    def save_chunks(self, chunks: list[TextChunk]) -> int: ...
    def delete_by_unit(self, subject: str, unit: str) -> int: ...
    def count_by_unit(self, subject: str, unit: str) -> int: ...
    def get_by_unit(self, subject: str, unit: str) -> list[TextChunk]: ...
    def vector_search(
        self,
        query_embedding: list[float],
        subject: str,
        unit: str | None = None,
        limit: int = 5,
    ) -> list[RetrievedChunk]: ...
    def keyword_search(
        self,
        query: str,
        subject: str,
        unit: str | None = None,
        limit: int = 5,
    ) -> list[RetrievedChunk]: ...
    def ensure_vector_index(self, dimensions: int) -> None: ...


class SessionRepository(Protocol):
    """Contract for study session persistence."""

    def save(self, session: StudySession) -> str: ...
    def get_by_id(self, session_id: str) -> StudySession | None: ...
    def get_recent(
        self, subject: str | None = None, limit: int = 10
    ) -> list[StudySession]: ...


class StudyGuideRepository(Protocol):
    """Contract for study guide caching."""

    def save(self, guide: StudyGuide) -> str: ...
    def get_by_unit(self, subject: str, unit: str) -> StudyGuide | None: ...
    def delete_by_unit(self, subject: str, unit: str) -> None: ...


class ExamRepository(Protocol):
    """Contract for exam persistence."""

    def save(self, exam: Exam) -> str: ...
    def get_by_id(self, exam_id: str) -> Exam | None: ...
    def get_by_subject(
        self, subject: str, limit: int = 20
    ) -> list[Exam]: ...
    def get_all(self, limit: int = 50) -> list[Exam]: ...


class AnalyticsRepository(Protocol):
    """Contract for analytics event logging and querying."""

    def log(self, event: AnalyticsEvent) -> str: ...
    def query(
        self,
        subject: str | None = None,
        event_type: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AnalyticsEvent]: ...


class UserRepository(Protocol):
    def save(self, stats: UserStats) -> str: ...
    def get_stats(self) -> UserStats | None: ...


class SettingsRepository(Protocol):
    def save(self, settings: AppSettings) -> str: ...
    def get(self) -> AppSettings: ...



class StudyProgressRepository(Protocol):
    def save(self, progress: StudyProgress) -> str: ...
    def get_by_unit(self, subject: str, unit: str) -> StudyProgress | None: ...
    def get_all(self, subject: str | None = None) -> list[StudyProgress]: ...


class WeakTopicRepository(Protocol):
    def save(self, weak_topic: WeakTopic) -> str: ...
    def get_by_topic(self, subject: str, unit: str, topic: str) -> WeakTopic | None: ...
    def get_weakest(self, limit: int = 10) -> list[WeakTopic]: ...


class PracticeSessionRepository(Protocol):
    def save(self, session: PracticeSession) -> str: ...
    def get_recent(self, limit: int = 10) -> list[PracticeSession]: ...


class ExamHistoryRepository(Protocol):
    def save(self, history: ExamHistory) -> str: ...
    def get_by_subject(self, subject: str) -> list[ExamHistory]: ...


class ExamTemplateRepository(Protocol):
    def save(self, template: ExamTemplate) -> str: ...
    def get_by_filename(self, filename: str) -> ExamTemplate | None: ...
    def get_by_subject(self, subject: str) -> list[ExamTemplate]: ...


# ═══════════════════════════════════════════════════════════════════════════
#  MongoDB Atlas Backend
# ═══════════════════════════════════════════════════════════════════════════


def _to_doc(model: Any) -> dict:
    """Convert a Pydantic model to a MongoDB-friendly dict."""
    d = model.model_dump(exclude={"id"})
    return d


def _from_doc(doc: dict, model_class: type) -> Any:
    """Convert a MongoDB document to a Pydantic model."""
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    # Remove internal MongoDB fields
    doc.pop("score", None)
    return model_class.model_validate(doc)


class MongoSubjectRepo:
    """MongoDB Atlas backend for subjects."""

    def __init__(self, collection: Collection) -> None:
        self._col = collection
        self._col.create_index("name", unique=True)

    def save(self, subject: Subject) -> str:
        doc = _to_doc(subject)
        result = self._col.insert_one(doc)
        return str(result.inserted_id)

    def get_by_name(self, name: str) -> Subject | None:
        doc = self._col.find_one({"name": name})
        return _from_doc(doc, Subject) if doc else None

    def get_all(self) -> list[Subject]:
        return [_from_doc(d, Subject) for d in self._col.find()]

    def update(self, subject: Subject) -> None:
        from bson import ObjectId

        if subject.id:
            self._col.replace_one(
                {"_id": ObjectId(subject.id)}, _to_doc(subject)
            )
        else:
            # Upsert by name
            self._col.replace_one(
                {"name": subject.name}, _to_doc(subject), upsert=True
            )

    def delete(self, subject_id: str) -> None:
        from bson import ObjectId

        self._col.delete_one({"_id": ObjectId(subject_id)})


class MongoChunkRepo:
    """
    MongoDB Atlas backend for text chunks with vector search.

    Chunks are stored with their embedding vectors in the 'chunks' collection.
    Uses MongoDB Atlas Vector Search ($vectorSearch aggregation stage)
    for semantic retrieval.
    """

    VECTOR_INDEX_NAME = "vector_index"

    def __init__(self, collection: Collection) -> None:
        self._col = collection
        # Create regular indexes for filtering
        self._col.create_index([("subject", 1), ("unit", 1)])

    def save_chunks(self, chunks: list[TextChunk]) -> int:
        if not chunks:
            return 0
        docs = [_to_doc(c) for c in chunks]
        result = self._col.insert_many(docs)
        return len(result.inserted_ids)

    def delete_by_unit(self, subject: str, unit: str) -> int:
        result = self._col.delete_many({"subject": subject, "unit": unit})
        return result.deleted_count

    def count_by_unit(self, subject: str, unit: str) -> int:
        return self._col.count_documents({"subject": subject, "unit": unit})

    def get_by_unit(self, subject: str, unit: str) -> list[TextChunk]:
        cursor = self._col.find({"subject": subject, "unit": unit}).sort("chunk_index", 1)
        return [_from_doc(d, TextChunk) for d in cursor]

    def vector_search(
        self,
        query_embedding: list[float],
        subject: str,
        unit: str | None = None,
        limit: int = 5,
    ) -> list[RetrievedChunk]:
        """
        Perform semantic search using MongoDB Atlas $vectorSearch.
        """
        filter_doc: dict[str, Any] = {"subject": subject}
        if unit:
            filter_doc["unit"] = unit

        pipeline: list[dict[str, Any]] = [
            {
                "$vectorSearch": {
                    "index": self.VECTOR_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": limit * 20,
                    "limit": limit,
                    "filter": filter_doc,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "text": 1,
                    "subject": 1,
                    "unit": 1,
                    "chunk_index": 1,
                    "page_range": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        try:
            results = list(self._col.aggregate(pipeline))
            return [
                RetrievedChunk(
                    text=r["text"],
                    subject=r["subject"],
                    unit=r["unit"],
                    chunk_index=r.get("chunk_index", 0),
                    page_range=r.get("page_range", ""),
                    score=r.get("score", 0.0),
                )
                for r in results
            ]
        except Exception as e:
            logger.warning("Vector search failed: %s. Falling back.", e)
            return []

    def keyword_search(
        self,
        query: str,
        subject: str,
        unit: str | None = None,
        limit: int = 5,
    ) -> list[RetrievedChunk]:
        """
        Fallback keyword search using MongoDB $regex.
        Used when vector search returns no results or scores are too low.
        """
        filter_doc: dict[str, Any] = {
            "subject": subject,
            "text": {"$regex": query, "$options": "i"},
        }
        if unit:
            filter_doc["unit"] = unit

        results = list(
            self._col.find(filter_doc, {"embedding": 0}).limit(limit)
        )
        return [
            RetrievedChunk(
                text=r["text"],
                subject=r["subject"],
                unit=r["unit"],
                chunk_index=r.get("chunk_index", 0),
                page_range=r.get("page_range", ""),
                score=0.5,  # arbitrary score for keyword matches
            )
            for r in results
        ]

    def ensure_vector_index(self, dimensions: int) -> None:
        """
        Ensure the Atlas Vector Search index exists.
        Creates it if missing.  This requires the Atlas cluster to be M10+
        or to have search enabled on an M0 free tier.
        """
        try:
            existing = list(self._col.list_search_indexes())
            for idx in existing:
                if idx.get("name") == self.VECTOR_INDEX_NAME:
                    logger.info("Vector index '%s' already exists.", self.VECTOR_INDEX_NAME)
                    return

            # Create the vector search index
            search_index = SearchIndexModel(
                definition={
                    "fields": [
                        {
                            "type": "vector",
                            "path": "embedding",
                            "numDimensions": dimensions,
                            "similarity": "cosine",
                        },
                        {
                            "type": "filter",
                            "path": "subject",
                        },
                        {
                            "type": "filter",
                            "path": "unit",
                        },
                    ]
                },
                name=self.VECTOR_INDEX_NAME,
                type="vectorSearch",
            )
            self._col.create_search_index(model=search_index)
            logger.info(
                "Created vector index '%s' with %d dimensions.",
                self.VECTOR_INDEX_NAME,
                dimensions,
            )
        except Exception as e:
            logger.warning(
                "Could not create vector index (may require Atlas M10+ or manual setup): %s",
                e,
            )


class MongoSessionRepo:
    """MongoDB Atlas backend for study sessions."""

    def __init__(self, collection: Collection) -> None:
        self._col = collection
        self._col.create_index([("subject", 1), ("started_at", -1)])

    def save(self, session: StudySession) -> str:
        doc = _to_doc(session)
        result = self._col.insert_one(doc)
        return str(result.inserted_id)

    def get_by_id(self, session_id: str) -> StudySession | None:
        from bson import ObjectId

        doc = self._col.find_one({"_id": ObjectId(session_id)})
        return _from_doc(doc, StudySession) if doc else None

    def get_recent(
        self, subject: str | None = None, limit: int = 10
    ) -> list[StudySession]:
        query: dict = {}
        if subject:
            query["subject"] = subject
        cursor = self._col.find(query).sort("started_at", -1).limit(limit)
        return [_from_doc(d, StudySession) for d in cursor]


class MongoStudyGuideRepo:
    """MongoDB Atlas backend for study guides."""

    def __init__(self, collection: Collection) -> None:
        self._col = collection
        self._col.create_index([("subject", 1), ("unit", 1)], unique=True)

    def save(self, guide: StudyGuide) -> str:
        # Upsert the study guide
        doc = _to_doc(guide)
        result = self._col.replace_one(
            {"subject": guide.subject, "unit": guide.unit}, doc, upsert=True
        )
        return str(result.upserted_id or "updated")

    def get_by_unit(self, subject: str, unit: str) -> StudyGuide | None:
        doc = self._col.find_one({"subject": subject, "unit": unit})
        return _from_doc(doc, StudyGuide) if doc else None
        
    def delete_by_unit(self, subject: str, unit: str) -> None:
        self._col.delete_one({"subject": subject, "unit": unit})


class MongoExamRepo:
    """MongoDB Atlas backend for exams."""

    def __init__(self, collection: Collection) -> None:
        self._col = collection
        self._col.create_index([("subject", 1), ("created_at", -1)])

    def save(self, exam: Exam) -> str:
        doc = _to_doc(exam)
        result = self._col.insert_one(doc)
        return str(result.inserted_id)

    def get_by_id(self, exam_id: str) -> Exam | None:
        from bson import ObjectId

        doc = self._col.find_one({"_id": ObjectId(exam_id)})
        return _from_doc(doc, Exam) if doc else None

    def get_by_subject(
        self, subject: str, limit: int = 20
    ) -> list[Exam]:
        cursor = (
            self._col.find({"subject": subject})
            .sort("created_at", -1)
            .limit(limit)
        )
        return [_from_doc(d, Exam) for d in cursor]

    def get_all(self, limit: int = 50) -> list[Exam]:
        cursor = self._col.find().sort("created_at", -1).limit(limit)
        return [_from_doc(d, Exam) for d in cursor]


class MongoAnalyticsRepo:
    """MongoDB Atlas backend for analytics events."""

    def __init__(self, collection: Collection) -> None:
        self._col = collection
        self._col.create_index([("event_type", 1), ("timestamp", -1)])
        self._col.create_index([("subject", 1), ("timestamp", -1)])

    def log(self, event: AnalyticsEvent) -> str:
        doc = _to_doc(event)
        result = self._col.insert_one(doc)
        return str(result.inserted_id)

    def query(
        self,
        subject: str | None = None,
        event_type: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AnalyticsEvent]:
        q: dict[str, Any] = {}
        if subject:
            q["subject"] = subject
        if event_type:
            q["event_type"] = event_type
        if since:
            q["timestamp"] = {"$gte": since}
        cursor = self._col.find(q).sort("timestamp", -1).limit(limit)
        return [_from_doc(d, AnalyticsEvent) for d in cursor]


class MongoUserRepo:
    def __init__(self, collection: Collection) -> None:
        self._col = collection

    def save(self, stats: UserStats) -> str:
        doc = _to_doc(stats)
        if stats.id:
            from bson import ObjectId
            self._col.replace_one({"_id": ObjectId(stats.id)}, doc)
            return stats.id
        else:
            result = self._col.insert_one(doc)
            return str(result.inserted_id)

    def get_stats(self) -> UserStats | None:
        doc = self._col.find_one()
        return _from_doc(doc, UserStats) if doc else None


class MongoSettingsRepo:
    def __init__(self, collection: Collection) -> None:
        self._col = collection

    def save(self, settings: AppSettings) -> str:
        doc = _to_doc(settings)
        if settings.id:
            self._col.replace_one({"_id": "global_settings"}, doc, upsert=True)
            return settings.id
        else:
            result = self._col.insert_one(doc)
            return str(result.inserted_id)

    def get(self) -> AppSettings:
        doc = self._col.find_one({"_id": "global_settings"})
        if doc:
            return _from_doc(doc, AppSettings)
        # return defaults if none exist
        return AppSettings(id="global")


class MongoStudyProgressRepo:
    def __init__(self, collection: Collection) -> None:
        self._col = collection
        self._col.create_index([("subject", 1), ("unit", 1)], unique=True)

    def save(self, progress: StudyProgress) -> str:
        doc = _to_doc(progress)
        result = self._col.replace_one(
            {"subject": progress.subject, "unit": progress.unit}, doc, upsert=True
        )
        return str(result.upserted_id or "updated")

    def get_by_unit(self, subject: str, unit: str) -> StudyProgress | None:
        doc = self._col.find_one({"subject": subject, "unit": unit})
        return _from_doc(doc, StudyProgress) if doc else None

    def get_all(self, subject: str | None = None) -> list[StudyProgress]:
        q = {"subject": subject} if subject else {}
        return [_from_doc(d, StudyProgress) for d in self._col.find(q)]


class MongoWeakTopicRepo:
    def __init__(self, collection: Collection) -> None:
        self._col = collection
        self._col.create_index([("subject", 1), ("unit", 1), ("topic", 1)], unique=True)
        self._col.create_index([("mastery_score", 1)])

    def save(self, weak_topic: WeakTopic) -> str:
        doc = _to_doc(weak_topic)
        result = self._col.replace_one(
            {"subject": weak_topic.subject, "unit": weak_topic.unit, "topic": weak_topic.topic},
            doc, upsert=True
        )
        return str(result.upserted_id or "updated")

    def get_by_topic(self, subject: str, unit: str, topic: str) -> WeakTopic | None:
        doc = self._col.find_one({"subject": subject, "unit": unit, "topic": topic})
        return _from_doc(doc, WeakTopic) if doc else None

    def get_weakest(self, limit: int = 10) -> list[WeakTopic]:
        cursor = self._col.find().sort("mastery_score", 1).limit(limit)
        return [_from_doc(d, WeakTopic) for d in cursor]


class MongoPracticeSessionRepo:
    def __init__(self, collection: Collection) -> None:
        self._col = collection
        self._col.create_index([("started_at", -1)])

    def save(self, session: PracticeSession) -> str:
        doc = _to_doc(session)
        result = self._col.insert_one(doc)
        return str(result.inserted_id)

    def get_recent(self, limit: int = 10) -> list[PracticeSession]:
        cursor = self._col.find().sort("started_at", -1).limit(limit)
        return [_from_doc(d, PracticeSession) for d in cursor]


class MongoExamHistoryRepo:
    def __init__(self, collection: Collection) -> None:
        self._col = collection
        self._col.create_index([("subject", 1), ("taken_at", -1)])

    def save(self, history: ExamHistory) -> str:
        doc = _to_doc(history)
        result = self._col.insert_one(doc)
        return str(result.inserted_id)

    def get_by_subject(self, subject: str) -> list[ExamHistory]:
        cursor = self._col.find({"subject": subject}).sort("taken_at", -1)
        return [_from_doc(d, ExamHistory) for d in cursor]


class MongoExamTemplateRepo:
    def __init__(self, collection: Collection) -> None:
        self._col = collection
        self._col.create_index([("filename", 1)], unique=True)

    def save(self, template: ExamTemplate) -> str:
        doc = _to_doc(template)
        result = self._col.replace_one(
            {"filename": template.filename}, doc, upsert=True
        )
        return str(result.upserted_id or "updated")

    def get_by_filename(self, filename: str) -> ExamTemplate | None:
        doc = self._col.find_one({"filename": filename})
        return _from_doc(doc, ExamTemplate) if doc else None

    def get_by_subject(self, subject: str) -> list[ExamTemplate]:
        cursor = self._col.find({"subject": subject})
        return [_from_doc(d, ExamTemplate) for d in cursor]


# ═══════════════════════════════════════════════════════════════════════════
#  In-Memory Backend (for testing / offline)
# ═══════════════════════════════════════════════════════════════════════════


class MemorySubjectRepo:
    """In-memory subject repository for testing."""

    def __init__(self) -> None:
        self._store: dict[str, Subject] = {}
        self._counter = 0

    def save(self, subject: Subject) -> str:
        self._counter += 1
        sid = str(self._counter)
        subject.id = sid
        self._store[sid] = subject
        return sid

    def get_by_name(self, name: str) -> Subject | None:
        for s in self._store.values():
            if s.name == name:
                return s
        return None

    def get_all(self) -> list[Subject]:
        return list(self._store.values())

    def update(self, subject: Subject) -> None:
        if subject.id:
            self._store[subject.id] = subject
        else:
            existing = self.get_by_name(subject.name)
            if existing and existing.id:
                subject.id = existing.id
                self._store[existing.id] = subject

    def delete(self, subject_id: str) -> None:
        self._store.pop(subject_id, None)


class MemoryChunkRepo:
    """In-memory chunk repository for testing."""

    def __init__(self) -> None:
        self._chunks: list[TextChunk] = []

    def save_chunks(self, chunks: list[TextChunk]) -> int:
        self._chunks.extend(chunks)
        return len(chunks)

    def delete_by_unit(self, subject: str, unit: str) -> int:
        before = len(self._chunks)
        self._chunks = [
            c
            for c in self._chunks
            if not (c.subject == subject and c.unit == unit)
        ]
        return before - len(self._chunks)

    def count_by_unit(self, subject: str, unit: str) -> int:
        return sum(
            1 for c in self._chunks if c.subject == subject and c.unit == unit
        )

    def get_by_unit(self, subject: str, unit: str) -> list[TextChunk]:
        chunks = [c for c in self._chunks if c.subject == subject and c.unit == unit]
        chunks.sort(key=lambda x: x.chunk_index)
        return chunks

    def vector_search(
        self,
        query_embedding: list[float],
        subject: str,
        unit: str | None = None,
        limit: int = 5,
    ) -> list[RetrievedChunk]:
        """Simple cosine similarity search over in-memory chunks."""
        import math

        filtered = [c for c in self._chunks if c.subject == subject]
        if unit:
            filtered = [c for c in filtered if c.unit == unit]

        def cosine_sim(a: list[float], b: list[float]) -> float:
            if not a or not b or len(a) != len(b):
                return 0.0
            dot = sum(x * y for x, y in zip(a, b))
            mag_a = math.sqrt(sum(x * x for x in a))
            mag_b = math.sqrt(sum(x * x for x in b))
            if mag_a == 0 or mag_b == 0:
                return 0.0
            return dot / (mag_a * mag_b)

        scored = [
            (c, cosine_sim(query_embedding, c.embedding)) for c in filtered
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [
            RetrievedChunk(
                text=c.text,
                subject=c.subject,
                unit=c.unit,
                chunk_index=c.chunk_index,
                page_range=c.page_range,
                score=score,
            )
            for c, score in scored[:limit]
        ]

    def keyword_search(
        self,
        query: str,
        subject: str,
        unit: str | None = None,
        limit: int = 5,
    ) -> list[RetrievedChunk]:
        query_lower = query.lower()
        filtered = [c for c in self._chunks if c.subject == subject]
        if unit:
            filtered = [c for c in filtered if c.unit == unit]
        matched = [c for c in filtered if query_lower in c.text.lower()]
        return [
            RetrievedChunk(
                text=c.text,
                subject=c.subject,
                unit=c.unit,
                chunk_index=c.chunk_index,
                page_range=c.page_range,
                score=0.5,
            )
            for c in matched[:limit]
        ]

    def ensure_vector_index(self, dimensions: int) -> None:
        pass  # No-op for in-memory


class MemorySessionRepo:
    def __init__(self) -> None:
        self._store: dict[str, StudySession] = {}
        self._counter = 0

    def save(self, session: StudySession) -> str:
        self._counter += 1
        sid = str(self._counter)
        session.id = sid
        self._store[sid] = session
        return sid

    def get_by_id(self, session_id: str) -> StudySession | None:
        return self._store.get(session_id)

    def get_recent(
        self, subject: str | None = None, limit: int = 10
    ) -> list[StudySession]:
        sessions = list(self._store.values())
        if subject:
            sessions = [s for s in sessions if s.subject == subject]
        sessions.sort(key=lambda s: s.started_at, reverse=True)
        return sessions[:limit]


class MemoryStudyGuideRepo:
    def __init__(self) -> None:
        self._store: dict[str, StudyGuide] = {}
        self._counter = 0

    def save(self, guide: StudyGuide) -> str:
        # Delete existing if any
        self.delete_by_unit(guide.subject, guide.unit)
        self._counter += 1
        gid = str(self._counter)
        guide.id = gid
        self._store[gid] = guide
        return gid

    def get_by_unit(self, subject: str, unit: str) -> StudyGuide | None:
        for g in self._store.values():
            if g.subject == subject and g.unit == unit:
                return g
        return None

    def delete_by_unit(self, subject: str, unit: str) -> None:
        to_del = [k for k, v in self._store.items() if v.subject == subject and v.unit == unit]
        for k in to_del:
            self._store.pop(k)


class MemoryExamRepo:
    def __init__(self) -> None:
        self._store: dict[str, Exam] = {}
        self._counter = 0

    def save(self, exam: Exam) -> str:
        self._counter += 1
        eid = str(self._counter)
        exam.id = eid
        self._store[eid] = exam
        return eid

    def get_by_id(self, exam_id: str) -> Exam | None:
        return self._store.get(exam_id)

    def get_by_subject(self, subject: str, limit: int = 20) -> list[Exam]:
        exams = [e for e in self._store.values() if e.subject == subject]
        exams.sort(key=lambda e: e.created_at, reverse=True)
        return exams[:limit]

    def get_all(self, limit: int = 50) -> list[Exam]:
        exams = list(self._store.values())
        exams.sort(key=lambda e: e.created_at, reverse=True)
        return exams[:limit]


class MemoryAnalyticsRepo:
    def __init__(self) -> None:
        self._events: list[AnalyticsEvent] = []

    def log(self, event: AnalyticsEvent) -> str:
        event.id = str(len(self._events) + 1)
        self._events.append(event)
        return event.id

    def query(
        self,
        subject: str | None = None,
        event_type: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AnalyticsEvent]:
        result = self._events[:]
        if subject:
            result = [e for e in result if e.subject == subject]
        if event_type:
            result = [e for e in result if e.event_type == event_type]
        if since:
            result = [e for e in result if e.timestamp >= since]
        result.sort(key=lambda e: e.timestamp, reverse=True)
        return result[:limit]


class MemoryUserRepo:
    def __init__(self) -> None:
        self._stats: UserStats | None = None

    def save(self, stats: UserStats) -> str:
        if not stats.id:
            stats.id = "1"
        self._stats = stats
        return stats.id

    def get_stats(self) -> UserStats | None:
        return self._stats


class MemorySettingsRepo:
    def __init__(self) -> None:
        self._settings: AppSettings | None = None

    def save(self, settings: AppSettings) -> str:
        if not settings.id:
            settings.id = "global"
        self._settings = settings
        return settings.id

    def get(self) -> AppSettings:
        if self._settings:
            return self._settings
        return AppSettings(id="global")


class MemoryStudyProgressRepo:
    def __init__(self) -> None:
        self._store: list[StudyProgress] = []

    def save(self, progress: StudyProgress) -> str:
        # Delete existing
        self._store = [p for p in self._store if not (p.subject == progress.subject and p.unit == progress.unit)]
        if not progress.id:
            progress.id = str(len(self._store) + 1)
        self._store.append(progress)
        return progress.id

    def get_by_unit(self, subject: str, unit: str) -> StudyProgress | None:
        for p in self._store:
            if p.subject == subject and p.unit == unit:
                return p
        return None

    def get_all(self, subject: str | None = None) -> list[StudyProgress]:
        if subject:
            return [p for p in self._store if p.subject == subject]
        return self._store[:]


class MemoryWeakTopicRepo:
    def __init__(self) -> None:
        self._store: list[WeakTopic] = []

    def save(self, weak_topic: WeakTopic) -> str:
        self._store = [t for t in self._store if not (t.subject == weak_topic.subject and t.unit == weak_topic.unit and t.topic == weak_topic.topic)]
        if not weak_topic.id:
            weak_topic.id = str(len(self._store) + 1)
        self._store.append(weak_topic)
        return weak_topic.id

    def get_by_topic(self, subject: str, unit: str, topic: str) -> WeakTopic | None:
        for t in self._store:
            if t.subject == subject and t.unit == unit and t.topic == topic:
                return t
        return None

    def get_weakest(self, limit: int = 10) -> list[WeakTopic]:
        s = sorted(self._store, key=lambda x: x.mastery_score)
        return s[:limit]


class MemoryPracticeSessionRepo:
    def __init__(self) -> None:
        self._store: list[PracticeSession] = []

    def save(self, session: PracticeSession) -> str:
        if not session.id:
            session.id = str(len(self._store) + 1)
        self._store.append(session)
        return session.id

    def get_recent(self, limit: int = 10) -> list[PracticeSession]:
        s = sorted(self._store, key=lambda x: x.started_at, reverse=True)
        return s[:limit]


class MemoryExamHistoryRepo:
    def __init__(self) -> None:
        self._store: list[ExamHistory] = []

    def save(self, history: ExamHistory) -> str:
        if not history.id:
            history.id = str(len(self._store) + 1)
        self._store.append(history)
        return history.id

    def get_by_subject(self, subject: str) -> list[ExamHistory]:
        s = [h for h in self._store if h.subject == subject]
        return sorted(s, key=lambda x: x.taken_at, reverse=True)


class MemoryExamTemplateRepo:
    def __init__(self) -> None:
        self._store: list[ExamTemplate] = []

    def save(self, template: ExamTemplate) -> str:
        self._store = [t for t in self._store if t.filename != template.filename]
        if not template.id:
            template.id = str(len(self._store) + 1)
        self._store.append(template)
        return template.id

    def get_by_filename(self, filename: str) -> ExamTemplate | None:
        for t in self._store:
            if t.filename == filename:
                return t
        return None

    def get_by_subject(self, subject: str) -> list[ExamTemplate]:
        return [t for t in self._store if t.subject == subject]


# ═══════════════════════════════════════════════════════════════════════════
#  Database Manager (Dependency Injection Container)
# ═══════════════════════════════════════════════════════════════════════════


class DatabaseManager:
    """
    Central database manager that provides access to all repositories.
    Acts as a dependency injection container — callers depend on the
    Protocol interfaces, not concrete backends.
    """

    def __init__(
        self,
        subjects: SubjectRepository,
        chunks: ChunkRepository,
        sessions: SessionRepository,
        study_guides: StudyGuideRepository,
        exams: ExamRepository,
        analytics: AnalyticsRepository,
        users: UserRepository,
        settings: SettingsRepository,
        progress: StudyProgressRepository,
        weak_topics: WeakTopicRepository,
        practice_sessions: PracticeSessionRepository,
        exam_history: ExamHistoryRepository,
        exam_templates: ExamTemplateRepository,
    ) -> None:
        self.subjects = subjects
        self.chunks = chunks
        self.sessions = sessions
        self.study_guides = study_guides
        self.exams = exams
        self.analytics = analytics
        self.users = users
        self.settings = settings
        self.progress = progress
        self.weak_topics = weak_topics
        self.practice_sessions = practice_sessions
        self.exam_history = exam_history
        self.exam_templates = exam_templates

    @classmethod
    def from_config(
        cls,
        backend: str = "mongodb",
        uri: str = "",
        db_name: str = "mca_study_suite",
    ) -> DatabaseManager:
        """
        Factory: create a DatabaseManager for the specified backend.

        Args:
            backend: "mongodb", "sqlite", or "memory"
            uri: Connection string (used for mongodb)
            db_name: Database name
        """
        if backend == "mongodb":
            return cls._create_mongo(uri, db_name)
        elif backend == "memory":
            return cls._create_memory()
        else:
            raise ValueError(f"Unsupported backend: {backend!r}")

    @classmethod
    def _create_mongo(cls, uri: str, db_name: str) -> DatabaseManager:
        """Create MongoDB Atlas-backed repositories."""
        if not uri:
            raise ValueError("MongoDB URI is required for 'mongodb' backend.")

        client = MongoClient(uri)
        db: Database = client[db_name]

        return cls(
            subjects=MongoSubjectRepo(db["subjects"]),
            chunks=MongoChunkRepo(db["chunks"]),
            sessions=MongoSessionRepo(db["study_sessions"]),
            study_guides=MongoStudyGuideRepo(db["study_guides"]),
            exams=MongoExamRepo(db["exams"]),
            analytics=MongoAnalyticsRepo(db["analytics"]),
            users=MongoUserRepo(db["users"]),
            settings=MongoSettingsRepo(db["settings"]),
            progress=MongoStudyProgressRepo(db["study_progress"]),
            weak_topics=MongoWeakTopicRepo(db["weak_topics"]),
            practice_sessions=MongoPracticeSessionRepo(db["practice_sessions"]),
            exam_history=MongoExamHistoryRepo(db["exam_history"]),
            exam_templates=MongoExamTemplateRepo(db["exam_templates"]),
        )

    @classmethod
    def _create_memory(cls) -> DatabaseManager:
        """Create in-memory repositories (for testing / offline use)."""
        return cls(
            subjects=MemorySubjectRepo(),
            chunks=MemoryChunkRepo(),
            sessions=MemorySessionRepo(),
            study_guides=MemoryStudyGuideRepo(),
            exams=MemoryExamRepo(),
            analytics=MemoryAnalyticsRepo(),
            users=MemoryUserRepo(),
            settings=MemorySettingsRepo(),
            progress=MemoryStudyProgressRepo(),
            weak_topics=MemoryWeakTopicRepo(),
            practice_sessions=MemoryPracticeSessionRepo(),
            exam_history=MemoryExamHistoryRepo(),
            exam_templates=MemoryExamTemplateRepo(),
        )
