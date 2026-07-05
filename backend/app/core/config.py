from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AI School Assistant API"
    api_v1_prefix: str = "/api/v1"
    env: str = "development"
    debug: bool = True
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
        ]
    )
    cors_origin_regex: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"

    database_url: str = "sqlite:///./school_assistant.db"
    sqlite_database_url: str = "sqlite:///./school_assistant.db"
    use_sqlite_for_dev: bool = False

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_embedding_model: str = "nomic-embed-text"
    openai_api_key: str | None = None
    openai_model: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_timeout_seconds: int = 60
    embedding_provider: str = "auto"
    embedding_model_name: str = "BAAI/bge-m3"
    sentence_transformer_model_name: str | None = None

    vector_db_provider: str = "chroma"
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection_name: str = "school_documents"

    max_upload_size_mb: int = 20
    allowed_upload_extensions: tuple[str, ...] = (".pdf", ".docx", ".txt")
    allowed_upload_mime_types: tuple[str, ...] = (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "application/octet-stream",
    )
    document_storage_dir: Path = DATA_DIR / "documents"
    rate_limit_per_minute: int = 60
    chat_memory_window: int = 6
    retrieval_k: int = 4
    chunk_size: int = 800
    chunk_overlap: int = 120
    seed_data_enabled: bool = True
    prewarm_embedding_model: bool = False

    @property
    def effective_database_url(self) -> str:
        if self.use_sqlite_for_dev:
            return self.sqlite_database_url
        return self.database_url

    @property
    def effective_embedding_provider(self) -> str:
        provider = self.embedding_provider.lower().strip()
        if provider == "auto":
            return "openai" if self.llm_provider.lower().strip() == "openai" else "ollama"
        return provider

    @property
    def effective_sentence_transformer_model_name(self) -> str:
        return self.sentence_transformer_model_name or self.embedding_model_name


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.document_storage_dir.mkdir(parents=True, exist_ok=True)
    return settings
