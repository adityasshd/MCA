"""
config — Application Configuration
====================================
Centralised configuration using pydantic-settings.  Reads from the .env
file in the project root and environment variables.

Usage:
    from src.core.config import get_config
    cfg = get_config()
    print(cfg.MONGODB_SERVER_URL)
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ── Paths ────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CHAPTERS_DIR = PROJECT_ROOT / "data" / "processed" / "chapters"
IMAGES_DIR = PROJECT_ROOT / "data" / "processed" / "images"


# ── Settings ─────────────────────────────────────────────────────────────


class AppConfig(BaseSettings):
    """
    Application settings loaded from .env and environment variables.
    Environment variables take precedence over .env values.
    """

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── MongoDB Atlas ──────────────────────────────────────────────────
    MONGODB_USERNAME: str = ""
    MONGODB_PASSWORD: str = ""
    MONGODB_SERVER_URL: str = ""
    MONGODB_AI_API_KEY: str = ""  # For MongoDB Atlas embedding / Voyage AI
    MONGODB_DB_NAME: str = "mca_study_suite"

    # ── Database backend ───────────────────────────────────────────────
    DB_BACKEND: Literal["mongodb", "sqlite", "memory"] = "mongodb"

    # ── LLM API keys ──────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # ── Kaggle remote API ─────────────────────────────────────────────
    KAGGLE_API_URL: str = ""  # Cloudflare tunnel URL from Kaggle notebook

    # ── Tier 1 (fast) model ────────────────────────────────────────────
    TIER1_PROVIDER: str = "ollama"
    TIER1_MODEL: str = "llama3.2:1b"

    # ── Tier 2 (reasoning) model ───────────────────────────────────────
    TIER2_PROVIDER: str = "ollama"
    TIER2_MODEL: str = "qwen2.5:1.5b"

    # ── Embedding ─────────────────────────────────────────────────────
    EMBEDDING_PROVIDER: Literal["local", "openai", "mongodb"] = "local"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    # OpenAI embedding model (used when EMBEDDING_PROVIDER=openai)
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMS: int = 1536
    # MongoDB / Voyage AI model (used when EMBEDDING_PROVIDER=mongodb)
    MONGODB_EMBEDDING_MODEL: str = "voyage-4-large"

    # ── RAG settings ──────────────────────────────────────────────────
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP_PCT: int = 10  # percentage
    RAG_TOP_K: int = 5
    VECTOR_SCORE_THRESHOLD: float = 0.5

    # ── Computed helpers ──────────────────────────────────────────────

    @property
    def chunk_overlap(self) -> int:
        """Actual overlap in characters."""
        return int(self.CHUNK_SIZE * self.CHUNK_OVERLAP_PCT / 100)

    @property
    def embedding_dimensions(self) -> int:
        """Return the dimensionality for the active embedding provider."""
        if self.EMBEDDING_PROVIDER == "local":
            return 384  # all-MiniLM-L6-v2
        elif self.EMBEDDING_PROVIDER == "openai":
            return self.OPENAI_EMBEDDING_DIMS
        elif self.EMBEDDING_PROVIDER == "mongodb":
            return 1024  # voyage-4-large default
        return 384


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Return a cached singleton of the application config."""
    return AppConfig()


def reload_config() -> AppConfig:
    """Force a reload of the configuration (clears cache)."""
    get_config.cache_clear()
    return get_config()
