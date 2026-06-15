"""
retriever — RAG Retrieval Engine
==================================
Handles semantic (vector) and keyword-based retrieval from MongoDB Atlas.

Strategy:
    1. Primary: MongoDB $vectorSearch using embeddings
    2. Fallback: Keyword regex search if vector results are below threshold
    3. Mismatch guard: Warns if stored chunks use a different embedding model
"""

from __future__ import annotations

import logging

from src.core.config import get_config
from src.core.database import DatabaseManager
from src.core.models import BaseEmbedder
from src.core.schemas import RetrievedChunk

logger = logging.getLogger(__name__)


class Retriever:
    """
    Hybrid retrieval engine combining vector search and keyword fallback.
    """

    def __init__(
        self,
        db: DatabaseManager,
        embedder: BaseEmbedder,
    ) -> None:
        self.db = db
        self.embedder = embedder
        self._config = get_config()

    def retrieve(
        self,
        query: str,
        subject: str,
        unit: str | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        """
        Retrieve relevant text chunks for a query.

        Uses vector search first, falls back to keyword search if
        vector results are insufficient or below the score threshold.

        Args:
            query: The user's question or search text
            subject: Subject name to search within
            unit: Optional unit name to narrow the search
            top_k: Number of results to return (defaults to config)

        Returns:
            List of RetrievedChunk objects sorted by relevance
        """
        if top_k is None:
            top_k = self._config.RAG_TOP_K

        # ── Vector Search ─────────────────────────────────────────────
        try:
            query_embedding = self.embedder.embed([query])[0]
            vector_results = self.db.chunks.vector_search(
                query_embedding=query_embedding,
                subject=subject,
                unit=unit,
                limit=top_k,
            )
        except Exception as e:
            logger.warning("Vector search failed: %s", e)
            vector_results = []

        # Check if vector results are good enough
        threshold = self._config.VECTOR_SCORE_THRESHOLD
        good_results = [r for r in vector_results if r.score >= threshold]

        if good_results:
            logger.debug(
                "Vector search returned %d results (>= %.2f threshold)",
                len(good_results),
                threshold,
            )
            return good_results

        # ── Keyword Fallback ──────────────────────────────────────────
        if not vector_results:
            logger.info(
                "Vector search returned no results for '%s'. "
                "Trying keyword search...",
                query[:50],
            )
            keyword_results = self.db.chunks.keyword_search(
                query=query,
                subject=subject,
                unit=unit,
                limit=top_k,
            )
            if keyword_results:
                logger.debug(
                    "Keyword search returned %d results.", len(keyword_results)
                )
                return keyword_results

            logger.info(
                "No results found for query in subject '%s'. "
                "Content may be outside the textbook scope.",
                subject,
            )
            return []

        # Return whatever vector results we have (below threshold)
        logger.debug(
            "Vector results below threshold (%.2f). "
            "Returning %d low-confidence results.",
            threshold,
            len(vector_results),
        )
        return vector_results

    def format_context(
        self,
        chunks: list[RetrievedChunk],
        max_chars: int = 4000,
    ) -> str:
        """
        Format retrieved chunks into a context string for LLM prompts.

        Args:
            chunks: List of retrieved chunks
            max_chars: Maximum total characters in the context

        Returns:
            Formatted context string with source annotations
        """
        if not chunks:
            return ""

        context_parts: list[str] = []
        total_chars = 0

        for i, chunk in enumerate(chunks, 1):
            source = f"[Source: {chunk.unit}, Pages {chunk.page_range}]"
            entry = f"--- Context {i} {source} ---\n{chunk.text}\n"

            if total_chars + len(entry) > max_chars:
                break

            context_parts.append(entry)
            total_chars += len(entry)

        return "\n".join(context_parts)
