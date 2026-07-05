from abc import ABC, abstractmethod


class LLMService(ABC):
    @abstractmethod
    def generate_answer(self, prompt: str, language: str) -> str:
        raise NotImplementedError


class EmbeddingService(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    def warmup(self) -> None:
        return None


class VectorStoreService(ABC):
    @abstractmethod
    def upsert_chunks(self, chunks: list[dict]) -> None:
        raise NotImplementedError

    @abstractmethod
    def chunk_search(self, query: str, limit: int = 4) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def delete_document(self, document_id: int) -> None:
        raise NotImplementedError
