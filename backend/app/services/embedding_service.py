from __future__ import annotations

import hashlib
import logging
from time import perf_counter

from app.core.config import get_settings
from app.services.interfaces import EmbeddingService


logger = logging.getLogger(__name__)


class SentenceTransformerEmbeddingService(EmbeddingService):
    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None

    @property
    def provider_name(self) -> str:
        return "sentence_transformers"

    @property
    def model_name(self) -> str:
        return self.settings.effective_sentence_transformer_model_name

    def _ensure_model(self):
        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import SentenceTransformer

            started_at = perf_counter()
            self._model = SentenceTransformer(self.model_name)
            logger.info(
                "Embedding model loaded: provider=%s model=%s load_seconds=%.2f",
                self.provider_name,
                self.model_name,
                perf_counter() - started_at,
            )
        except Exception as exc:  # pragma: no cover - fallback path
            logger.warning(
                "Falling back to hash embeddings because the local embedding model is unavailable: %s",
                exc,
            )
            self._model = False
        return self._model

    def warmup(self) -> None:
        model = self._ensure_model()
        if not model:
            logger.warning("Skipping sentence-transformer warmup because fallback hash embeddings are active")
            return

        started_at = perf_counter()
        model.encode(["warmup"], normalize_embeddings=True)
        logger.info(
            "Embedding model warmup complete: provider=%s model=%s warmup_seconds=%.2f",
            self.provider_name,
            self.model_name,
            perf_counter() - started_at,
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        model = self._ensure_model()
        if model:
            vectors = model.encode(texts, normalize_embeddings=True)
            return [vector.tolist() for vector in vectors]

        fallback_vectors: list[list[float]] = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            fallback_vectors.append([byte / 255 for byte in digest[:32]])
        return fallback_vectors


class OpenAIEmbeddingService(EmbeddingService):
    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER resolves to openai")

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self.settings.openai_embedding_model

    def warmup(self) -> None:
        logger.info(
            "Skipping embedding warmup call for provider=%s model=%s to avoid unnecessary API usage",
            self.provider_name,
            self.model_name,
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        from openai import OpenAI

        client = OpenAI(
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url,
            timeout=self.settings.openai_timeout_seconds,
        )
        response = client.embeddings.create(model=self.model_name, input=texts)
        return [item.embedding for item in response.data]


class OllamaEmbeddingService(EmbeddingService):
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self.settings.ollama_embedding_model

    def warmup(self) -> None:
        started_at = perf_counter()
        self.embed_texts(["warmup"])
        logger.info(
            "Embedding model warmup complete: provider=%s model=%s warmup_seconds=%.2f",
            self.provider_name,
            self.model_name,
            perf_counter() - started_at,
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        from ollama import Client

        client = Client(host=self.settings.ollama_base_url)
        embed_method = getattr(client, "embed", None)
        if callable(embed_method):
            response = embed_method(model=self.model_name, input=texts)
            return response["embeddings"]

        # Older ollama Python clients expose `embeddings()` one prompt at a time.
        return [client.embeddings(model=self.model_name, prompt=text)["embedding"] for text in texts]


def get_embedding_service() -> EmbeddingService:
    settings = get_settings()
    provider = settings.effective_embedding_provider
    if provider == "openai":
        return OpenAIEmbeddingService()
    if provider == "ollama":
        return OllamaEmbeddingService()
    if provider == "sentence_transformers":
        return SentenceTransformerEmbeddingService()
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {settings.embedding_provider}")
