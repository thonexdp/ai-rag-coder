from app.core.config import get_settings
from app.schemas.chat import ChatSource
from app.services.vector_store import ChromaVectorStoreService


class Retriever:
    def __init__(self, vector_store: ChromaVectorStoreService):
        self.vector_store = vector_store
        self.settings = get_settings()

    def search(self, query: str) -> list[ChatSource]:
        results = self.vector_store.chunk_search(query, limit=self.settings.retrieval_k)
        return [
            ChatSource(
                document_id=item["metadata"].get("document_id"),
                title=item["metadata"].get("title", "Unknown document"),
                snippet=item["content"][:280],
                page=item["metadata"].get("page"),
                source_type=item["metadata"].get("source_type", "document"),
            )
            for item in results
        ]
