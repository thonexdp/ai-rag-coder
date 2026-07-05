from app.core.config import get_settings
from app.services.embedding_service import (
    OllamaEmbeddingService,
    OpenAIEmbeddingService,
    SentenceTransformerEmbeddingService,
    get_embedding_service,
)
from app.services.vector_store import ChromaVectorStoreService


def _reset_settings_cache():
    get_settings.cache_clear()


def test_embedding_provider_auto_resolves_to_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "auto")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    _reset_settings_cache()

    service = get_embedding_service()

    assert isinstance(service, OpenAIEmbeddingService)


def test_embedding_provider_auto_resolves_to_ollama(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "auto")
    monkeypatch.setenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    _reset_settings_cache()

    service = get_embedding_service()

    assert isinstance(service, OllamaEmbeddingService)


def test_embedding_provider_sentence_transformers_override(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "sentence_transformers")
    monkeypatch.setenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")
    _reset_settings_cache()

    service = get_embedding_service()

    assert isinstance(service, SentenceTransformerEmbeddingService)


def test_chroma_collection_name_changes_with_provider_and_model(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "auto")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    _reset_settings_cache()

    vector_store = ChromaVectorStoreService(embedding_service=get_embedding_service())

    assert vector_store.collection_name == "school_documents__openai__text_embedding_3_small"
