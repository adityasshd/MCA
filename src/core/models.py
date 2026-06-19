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

    @classmethod
    def get_available_models(cls, api_key: str = "") -> list[str]:
        """Fetch available models from the provider."""
        return []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model!r})"


class GroqProvider(BaseLLM):
    """Groq Cloud inference — DEFAULT provider."""

    def __init__(self, model: str, api_key: str) -> None:
        super().__init__(model, api_key)
        from groq import Groq

        self._client = Groq(api_key=api_key)

    @classmethod
    def get_available_models(cls, api_key: str = "") -> list[str]:
        if not api_key:
            return []
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            models = client.models.list()
            return [m.id for m in models.data]
        except Exception as e:
            logger.warning(f"Failed to fetch Groq models: {e}")
            return ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]

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

    @classmethod
    def get_available_models(cls, api_key: str = "") -> list[str]:
        if not api_key:
            return []
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            models = client.models.list()
            # filter to chat models
            return sorted([m.id for m in models.data if "gpt" in m.id or "o1" in m.id])
        except Exception as e:
            logger.warning(f"Failed to fetch OpenAI models: {e}")
            return ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]

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

    @classmethod
    def get_available_models(cls, api_key: str = "") -> list[str]:
        if not api_key:
            return []
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            models = list(client.models.list())
            return sorted([m.name.replace("models/", "") for m in models if "generateContent" in m.supported_actions])
        except Exception as e:
            logger.warning(f"Failed to fetch Gemini models: {e}")
            return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]

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


class OpenRouterProvider(BaseLLM):
    """OpenRouter API provider."""

    def __init__(self, model: str, api_key: str) -> None:
        super().__init__(model, api_key)
        from openai import OpenAI
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

    @classmethod
    def get_available_models(cls, api_key: str = "") -> list[str]:
        try:
            response = requests.get("https://openrouter.ai/api/v1/models")
            response.raise_for_status()
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
        except Exception as e:
            logger.warning(f"Failed to fetch OpenRouter models: {e}")
            return ["anthropic/claude-3-haiku", "anthropic/claude-3-opus", "google/gemini-pro"]

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
            raise LLMError(f"OpenRouter API error: {e}") from e

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
            raise LLMError(f"OpenRouter streaming error: {e}") from e


class OllamaProvider(BaseLLM):
    """Local Ollama instance provider (fallback)."""

    def __init__(self, model: str, api_key: str = "") -> None:
        super().__init__(model, api_key)

    @classmethod
    def get_available_models(cls, api_key: str = "") -> list[str]:
        try:
            from ollama import list as ollama_list
            models = ollama_list()
            return [m.model for m in models.get("models", [])] if isinstance(models, dict) else [m.model for m in models]
        except Exception as e:
            logger.warning(f"Failed to fetch Ollama models: {e}")
            return ["llama3.2:1b", "qwen2.5:1.5b", "phi3"]

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

    @classmethod
    def get_available_models(cls, api_key: str = "") -> list[str]:
        # Currently hardcoded to known kaggle models we run on our T4 notebook
        return [
            "google/gemma-1.1-2b-it",
            "meta-llama/Llama-3.2-1B-Instruct",
            "Qwen/Qwen2.5-1.5B-Instruct",
            "anthropic/claude-haiku-4-5@20251001",
            "anthropic/claude-opus-4-1@20250805",
            "anthropic/claude-opus-4-5@20251101",
            "anthropic/claude-opus-4-6@default",
            "anthropic/claude-opus-4-7@default",
            "anthropic/claude-opus-4-8@default",
            "anthropic/claude-sonnet-4-5@20250929",
            "anthropic/claude-sonnet-4-6@default",
            "anthropic/claude-sonnet-4@20250514",
            "deepseek-ai/deepseek-r1-0528",
            "deepseek-ai/deepseek-v3.1",
            "deepseek-ai/deepseek-v3.2",
            "google/gemini-2.5-flash",
            "google/gemini-2.5-pro",
            "google/gemini-3-flash-preview",
            "google/gemini-3.1-flash-lite-preview",
            "google/gemini-3.1-pro-preview",
            "google/gemini-3.5-flash",
            "google/gemma-4-26b-a4b",
            "google/gemma-4-31b",
            "openai/gpt-5.4-2026-03-05",
            "openai/gpt-5.4-mini-2026-03-17",
            "openai/gpt-5.4-nano-2026-03-17",
            "openai/gpt-5.5-2026-04-23",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3-235b-a22b-instruct-2507",
            "qwen/qwen3-coder-480b-a35b-instruct",
            "qwen/qwen3-next-80b-a3b-instruct",
            "qwen/qwen3-next-80b-a3b-thinking",
            "xai/grok-4.20-0309-non-reasoning",
            "xai/grok-4.20-0309-reasoning",
            "zai/glm-5"
        ]

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
    "openrouter": OpenRouterProvider,
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
    Manages the task-specific LLM system and the active embedding provider.
    Supports fetching the correct model based on the task from database settings.
    """

    def __init__(
        self,
        db,
        embedder: BaseEmbedder,
    ) -> None:
        self.db = db
        self.embedder = embedder

    @classmethod
    def from_db(cls, db, config) -> ModelManager:
        """Create a ModelManager using database settings."""
        settings = db.settings.get()

        # Embedding provider (still partly uses config for defaults/provider choice)
        embed_key_map = {
            "local": "",
            "openai": settings.api_keys.get("openai", ""),
            "mongodb": settings.api_keys.get("mongodb", ""),
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

        return cls(db=db, embedder=embedder)

    def _get_llm_for_task(self, task: str) -> BaseLLM:
        settings = self.db.settings.get()
        assignment = settings.task_models.get(task)
        if not assignment:
            # Fallback
            provider = "ollama"
            model = "llama3.2:1b"
            api_key = ""
        else:
            provider = assignment.provider
            model = assignment.model
            api_key = settings.api_keys.get(provider, "")
            
        return create_llm(provider=provider, model=model, api_key=api_key)

    @property
    def fast(self) -> BaseLLM:
        return self._get_llm_for_task("tutor")

    @property
    def thinking(self) -> BaseLLM:
        return self._get_llm_for_task("exam")

    def get_tutor_llm(self) -> BaseLLM:
        return self._get_llm_for_task("tutor")

    def get_practice_llm(self) -> BaseLLM:
        return self._get_llm_for_task("practice")

    def get_exam_llm(self) -> BaseLLM:
        return self._get_llm_for_task("exam")

    def get_study_guide_llm(self) -> BaseLLM:
        return self._get_llm_for_task("study_guide")

    def get_analytics_llm(self) -> BaseLLM:
        return self._get_llm_for_task("analytics")

    def swap_llm(
        self, task: str, provider: str, model: str, api_key: str = ""
    ) -> None:
        """Update the model assignment for a task."""
        settings = self.db.settings.get()
        from src.core.schemas import ModelAssignment
        settings.task_models[task] = ModelAssignment(provider=provider, model=model)
        if api_key:
            settings.api_keys[provider] = api_key
        self.db.settings.save(settings)
        logger.info("Updated task '%s' to use %s/%s", task, provider, model)

    def swap_embedder(
        self, provider: str, api_key: str = "", model: str = ""
    ) -> None:
        """Hot-swap the embedding provider."""
        self.embedder = create_embedder(provider, api_key, model)
        logger.info("Swapped embedder to %s", self.embedder.model_name)
