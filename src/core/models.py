"""
models — Swappable LLM & Embedding Providers
==============================================
Abstract provider pattern for both LLM inference and embedding generation.

LLM Tiers:
    Tier 1 (fast)      — quick responses, intent detection, simple grading
    Tier 2 (reasoning) — complex feedback, exam generation, essay grading

Embedding Providers:
    local    — sentence-transformers (all-MiniLM-L6-v2, 384-dim, free)
    openai   — text-embedding-3-small (1536-dim, API key required)
    mongodb  — MongoDB Atlas Voyage AI (via ai.mongodb.com API)

All providers can be hot-swapped at runtime without restarting the app.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Iterator

import requests

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
#  LLM Providers
# ═══════════════════════════════════════════════════════════════════════════


class LLMError(Exception):
    """Raised when an LLM call fails."""

    pass


class BaseLLM(ABC):
    """Abstract base for all LLM providers."""

    def __init__(self, model: str, api_key: str = "") -> None:
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate a complete response."""
        ...

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Iterator[str]:
        """Generate a streaming response, yielding chunks."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model!r})"


class GroqProvider(BaseLLM):
    """Groq Cloud inference — DEFAULT provider."""

    def __init__(self, model: str, api_key: str) -> None:
        super().__init__(model, api_key)
        from groq import Groq

        self._client = Groq(api_key=api_key)

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise LLMError(f"Groq API error: {e}") from e

    def generate_stream(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Iterator[str]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            raise LLMError(f"Groq streaming error: {e}") from e


class OpenAIProvider(BaseLLM):
    """OpenAI API provider."""

    def __init__(self, model: str, api_key: str) -> None:
        super().__init__(model, api_key)
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise LLMError(f"OpenAI API error: {e}") from e

    def generate_stream(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Iterator[str]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            raise LLMError(f"OpenAI streaming error: {e}") from e


class GeminiProvider(BaseLLM):
    """Google Gemini API provider."""

    def __init__(self, model: str, api_key: str) -> None:
        super().__init__(model, api_key)
        from google import genai

        self._client = genai.Client(api_key=api_key)

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        try:
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            response = self._client.models.generate_content(
                model=self.model,
                contents=full_prompt,
            )
            return response.text or ""
        except Exception as e:
            raise LLMError(f"Gemini API error: {e}") from e

    def generate_stream(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Iterator[str]:
        # Gemini streaming — yield full response as single chunk for now
        yield self.generate(prompt, system, temperature, max_tokens)


class OllamaProvider(BaseLLM):
    """Local Ollama instance provider (fallback)."""

    def __init__(self, model: str, api_key: str = "") -> None:
        super().__init__(model, api_key)

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        try:
            from ollama import chat

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            response = chat(model=self.model, messages=messages)
            return response.message.content or ""
        except Exception as e:
            raise LLMError(f"Ollama error: {e}") from e

    def generate_stream(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Iterator[str]:
        try:
            from ollama import chat

            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            stream = chat(model=self.model, messages=messages, stream=True)
            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
        except Exception as e:
            raise LLMError(f"Ollama streaming error: {e}") from e


class KaggleProvider(BaseLLM):
    """Remote Kaggle notebook provider — sends requests to a FastAPI endpoint."""

    def __init__(self, model: str, api_key: str = "") -> None:
        super().__init__(model, api_key)
        # api_key is reused to hold the base URL of the Kaggle tunnel
        self._base_url = api_key.rstrip("/")
        if not self._base_url:
            raise LLMError(
                "KaggleProvider requires KAGGLE_API_URL to be set. "
                "This should be the Cloudflare tunnel URL from your Kaggle notebook."
            )

    def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        try:
            response = requests.post(
                f"{self._base_url}/generate",
                json={
                    "prompt": prompt,
                    "system": system,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise LLMError(f"Kaggle API returned an error: {data['error']}")
            return data.get("response", "")
        except requests.exceptions.ConnectionError:
            raise LLMError(
                f"Cannot reach Kaggle API at {self._base_url}. "
                "Is the Kaggle notebook still running?"
            )
        except Exception as e:
            raise LLMError(f"Kaggle API error: {e}") from e

    def generate_stream(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Iterator[str]:
        # Kaggle endpoint doesn't support streaming — yield full response
        yield self.generate(prompt, system, temperature, max_tokens)


# ═══════════════════════════════════════════════════════════════════════════
#  Embedding Providers
# ═══════════════════════════════════════════════════════════════════════════


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""

    pass


class BaseEmbedder(ABC):
    """Abstract base for embedding providers."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding dimensionality."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier string."""
        ...


class LocalEmbedder(BaseEmbedder):
    """Local sentence-transformers embeddings (free, no API key)."""

    def __init__(self, model: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model
        self._model = None  # lazy-loaded

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading local embedding model: %s", self._model_name)
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            model = self._load_model()
            embeddings = model.encode(texts, show_progress_bar=False)
            return [e.tolist() for e in embeddings]
        except Exception as e:
            raise EmbeddingError(f"Local embedding error: {e}") from e

    @property
    def dimension(self) -> int:
        return 384

    @property
    def model_name(self) -> str:
        return self._model_name


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI text-embedding-3-small embeddings."""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimensions: int = 1536,
    ) -> None:
        from openai import OpenAI

        self._client = OpenAI(api_key=api_key)
        self._model_name = model
        self._dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self._client.embeddings.create(
                input=texts,
                model=self._model_name,
                dimensions=self._dimensions,
            )
            return [d.embedding for d in response.data]
        except Exception as e:
            raise EmbeddingError(f"OpenAI embedding error: {e}") from e

    @property
    def dimension(self) -> int:
        return self._dimensions

    @property
    def model_name(self) -> str:
        return self._model_name


class MongoDBEmbedder(BaseEmbedder):
    """
    MongoDB Atlas Voyage AI embeddings via ai.mongodb.com API.
    Uses the MONGODB_AI_API_KEY for authentication.
    """

    ENDPOINT = "https://ai.mongodb.com/v1/embeddings"

    def __init__(
        self,
        api_key: str,
        model: str = "voyage-4-large",
    ) -> None:
        self._api_key = api_key
        self._model_name = model
        # Voyage model dimension mapping
        self._dim_map = {
            "voyage-4-large": 1024,
            "voyage-4": 1024,
            "voyage-4-lite": 512,
            "voyage-multimodal-3.5": 1024,
        }

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "input": texts,
                "model": self._model_name,
            }
            response = requests.post(
                self.ENDPOINT,
                headers=headers,
                data=json.dumps(payload),
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
        except Exception as e:
            raise EmbeddingError(f"MongoDB embedding error: {e}") from e

    @property
    def dimension(self) -> int:
        return self._dim_map.get(self._model_name, 1024)

    @property
    def model_name(self) -> str:
        return self._model_name


# ═══════════════════════════════════════════════════════════════════════════
#  Model Manager (Central Orchestrator)
# ═══════════════════════════════════════════════════════════════════════════

# Provider registry
LLM_PROVIDERS: dict[str, type[BaseLLM]] = {
    "groq": GroqProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
    "kaggle": KaggleProvider,
}


def create_llm(provider: str, model: str, api_key: str = "") -> BaseLLM:
    """Factory: create an LLM provider instance."""
    cls = LLM_PROVIDERS.get(provider)
    if not cls:
        raise ValueError(
            f"Unknown LLM provider: {provider!r}. "
            f"Available: {list(LLM_PROVIDERS.keys())}"
        )
    return cls(model=model, api_key=api_key)


def create_embedder(
    provider: str,
    api_key: str = "",
    model: str = "",
) -> BaseEmbedder:
    """Factory: create an embedding provider instance."""
    if provider == "local":
        return LocalEmbedder(model=model or "all-MiniLM-L6-v2")
    elif provider == "openai":
        return OpenAIEmbedder(
            api_key=api_key,
            model=model or "text-embedding-3-small",
        )
    elif provider == "mongodb":
        return MongoDBEmbedder(
            api_key=api_key,
            model=model or "voyage-4-large",
        )
    else:
        raise ValueError(f"Unknown embedding provider: {provider!r}")


class ModelManager:
    """
    Manages the two-tier LLM system and the active embedding provider.
    Supports hot-swapping providers at runtime.
    """

    def __init__(
        self,
        fast: BaseLLM,
        thinking: BaseLLM,
        embedder: BaseEmbedder,
    ) -> None:
        self.fast = fast
        self.thinking = thinking
        self.embedder = embedder

    @classmethod
    def from_config(cls, config) -> ModelManager:
        """Create a ModelManager from an AppConfig instance."""
        # Resolve API keys for each provider
        key_map = {
            "groq": config.GROQ_API_KEY,
            "openai": config.OPENAI_API_KEY,
            "gemini": config.GEMINI_API_KEY,
            "ollama": "",
            "kaggle": config.KAGGLE_API_URL,
        }

        fast = create_llm(
            provider=config.TIER1_PROVIDER,
            model=config.TIER1_MODEL,
            api_key=key_map.get(config.TIER1_PROVIDER, ""),
        )
        thinking = create_llm(
            provider=config.TIER2_PROVIDER,
            model=config.TIER2_MODEL,
            api_key=key_map.get(config.TIER2_PROVIDER, ""),
        )

        # Embedding provider
        embed_key_map = {
            "local": "",
            "openai": config.OPENAI_API_KEY,
            "mongodb": config.MONGODB_AI_API_KEY,
        }
        embedder = create_embedder(
            provider=config.EMBEDDING_PROVIDER,
            api_key=embed_key_map.get(config.EMBEDDING_PROVIDER, ""),
            model=(
                config.EMBEDDING_MODEL
                if config.EMBEDDING_PROVIDER == "local"
                else (
                    config.OPENAI_EMBEDDING_MODEL
                    if config.EMBEDDING_PROVIDER == "openai"
                    else config.MONGODB_EMBEDDING_MODEL
                )
            ),
        )

        return cls(fast=fast, thinking=thinking, embedder=embedder)

    def swap_llm(
        self, tier: str, provider: str, model: str, api_key: str = ""
    ) -> None:
        """Hot-swap an LLM provider for a given tier."""
        new_llm = create_llm(provider, model, api_key)
        if tier == "fast":
            self.fast = new_llm
        elif tier == "thinking":
            self.thinking = new_llm
        else:
            raise ValueError(f"Unknown tier: {tier!r}. Use 'fast' or 'thinking'.")
        logger.info("Swapped %s tier to %s", tier, new_llm)

    def swap_embedder(
        self, provider: str, api_key: str = "", model: str = ""
    ) -> None:
        """Hot-swap the embedding provider."""
        self.embedder = create_embedder(provider, api_key, model)
        logger.info("Swapped embedder to %s", self.embedder.model_name)
