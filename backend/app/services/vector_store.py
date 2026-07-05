from __future__ import annotations

import logging
import re
from time import perf_counter
from typing import Any

import chromadb

from app.core.config import get_settings
from app.services.embedding_service import get_embedding_service
from app.services.interfaces import EmbeddingService, VectorStoreService


logger = logging.getLogger(__name__)


class ChromaVectorStoreService(VectorStoreService):
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.settings = get_settings()
        self.embedding_service = embedding_service or get_embedding_service()
        self.collection_name = self._build_collection_name()
        self._collection = None

    def _build_collection_name(self) -> str:
        def sanitize(value: str) -> str:
            return re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()

        return "__".join(
            (
                sanitize(self.settings.chroma_collection_name),
                sanitize(self.embedding_service.provider_name),
                sanitize(self.embedding_service.model_name),
            )
        )

    def _get_collection(self):
        if self._collection is not None:
            return self._collection

        try:
            started_at = perf_counter()
            client = chromadb.HttpClient(host=self.settings.chroma_host, port=self.settings.chroma_port)
            logger.info(
                "Connected to remote Chroma: host=%s port=%s connect_seconds=%.2f",
                self.settings.chroma_host,
                self.settings.chroma_port,
                perf_counter() - started_at,
            )
        except Exception:  # pragma: no cover - fallback path
            logger.warning("Falling back to local Chroma client storage")
            client = chromadb.Client()
        self._collection = client.get_or_create_collection(name=self.collection_name)
        logger.info(
            "Using Chroma collection: name=%s provider=%s model=%s",
            self.collection_name,
            self.embedding_service.provider_name,
            self.embedding_service.model_name,
        )
        return self._collection

    def upsert_chunks(self, chunks: list[dict[str, Any]]) -> None:
        if not chunks:
            return
        collection = self._get_collection()
        documents = [chunk["content"] for chunk in chunks]
        started_at = perf_counter()
        embeddings = self.embedding_service.embed_texts(documents)
        embedding_seconds = perf_counter() - started_at
        upsert_started_at = perf_counter()
        collection.upsert(
            ids=[chunk["id"] for chunk in chunks],
            documents=documents,
            metadatas=[chunk["metadata"] for chunk in chunks],
            embeddings=embeddings,
        )
        logger.info(
            "Chroma upsert complete: collection=%s provider=%s model=%s chunks=%s embedding_seconds=%.2f upsert_seconds=%.2f",
            self.collection_name,
            self.embedding_service.provider_name,
            self.embedding_service.model_name,
            len(chunks),
            embedding_seconds,
            perf_counter() - upsert_started_at,
        )

    def chunk_search(self, query: str, limit: int = 4) -> list[dict[str, Any]]:
        collection = self._get_collection()
        embedding = self.embedding_service.embed_texts([query])[0]
        results = collection.query(query_embeddings=[embedding], n_results=limit)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        ids = results.get("ids", [[]])[0]
        return [
            {"id": item_id, "content": document, "metadata": metadata}
            for item_id, document, metadata in zip(ids, documents, metadatas, strict=False)
        ]

    def delete_document(self, document_id: int) -> None:
        collection = self._get_collection()
        collection.delete(where={"document_id": document_id})
