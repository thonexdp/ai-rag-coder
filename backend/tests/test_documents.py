import asyncio
from io import BytesIO

from fastapi import UploadFile
from starlette.datastructures import Headers

from app.core.security import get_password_hash
from app.database.models import Document, DocumentStatus, User, UserRole
from app.services.document_service import DocumentIngestionService
from app.services.interfaces import EmbeddingService


class _FakeEmbeddingService(EmbeddingService):
    def __init__(self, provider_name: str, model_name: str):
        self._provider_name = provider_name
        self._model_name = model_name
        self.calls: list[list[str]] = []

    @property
    def provider_name(self) -> str:
        return self._provider_name

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(texts)
        return [[0.1, 0.2, 0.3] for _ in texts]


class _FakeCollection:
    def __init__(self):
        self.upserts = []

    def upsert(self, **kwargs):
        self.upserts.append(kwargs)

    def delete(self, **kwargs):
        return None


def _make_upload_file(filename: str, content: bytes, content_type: str) -> UploadFile:
    return UploadFile(
        file=BytesIO(content),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


def _admin_user(db_session):
    admin = User(
        email="admin-service@test.local",
        full_name="Admin Service Test",
        hashed_password=get_password_hash("AdminPass123"),
        role=UserRole.admin,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


def _admin_token(client, db_session):
    admin = User(
        email="admin@test.local",
        full_name="Admin Test",
        hashed_password=get_password_hash("AdminPass123"),
        role=UserRole.admin,
    )
    db_session.add(admin)
    db_session.commit()
    response = client.post("/api/v1/auth/login", json={"email": admin.email, "password": "AdminPass123"})
    return response.json()["access_token"]


def test_admin_can_upload_txt_document(client, db_session):
    token = _admin_token(client, db_session)
    response = client.post(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("handbook.txt", b"Enrollment starts on Monday.", "text/plain")},
        data={"title": "School Handbook"},
    )
    assert response.status_code == 200
    assert response.json()["status"] in {"pending", "processing", "ready"}


def test_non_admin_cannot_upload_document(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "student@test.local",
            "full_name": "Student Test",
            "password": "StudentPass123",
            "role": "student",
        },
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": "student@test.local", "password": "StudentPass123"}
    )
    token = login.json()["access_token"]
    response = client.post(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("handbook.txt", b"Enrollment starts on Monday.", "text/plain")},
    )
    assert response.status_code == 403


def test_document_ingestion_ready_with_mocked_openai_embeddings(db_session, tmp_path):
    admin = _admin_user(db_session)
    embedding_service = _FakeEmbeddingService("openai", "text-embedding-3-small")
    service = DocumentIngestionService(db_session, embedding_service=embedding_service)
    service.settings.document_storage_dir = tmp_path
    fake_collection = _FakeCollection()
    service.vector_store._get_collection = lambda: fake_collection

    upload = _make_upload_file("handbook.txt", b"Enrollment starts on Monday.", "text/plain")
    document = asyncio.run(service.save_upload(upload, "School Handbook", admin))
    service.process_document(document.id)

    db_session.expire_all()
    stored_document = db_session.get(Document, document.id)
    assert stored_document is not None
    assert stored_document.status == DocumentStatus.ready
    assert embedding_service.calls
    assert fake_collection.upserts


def test_document_ingestion_ready_with_mocked_ollama_embeddings(db_session, tmp_path):
    admin = _admin_user(db_session)
    embedding_service = _FakeEmbeddingService("ollama", "nomic-embed-text")
    service = DocumentIngestionService(db_session, embedding_service=embedding_service)
    service.settings.document_storage_dir = tmp_path
    fake_collection = _FakeCollection()
    service.vector_store._get_collection = lambda: fake_collection

    upload = _make_upload_file("schedule.txt", b"Classes begin at 8 AM.", "text/plain")
    document = asyncio.run(service.save_upload(upload, "Schedule", admin))
    service.process_document(document.id)

    db_session.expire_all()
    stored_document = db_session.get(Document, document.id)
    assert stored_document is not None
    assert stored_document.status == DocumentStatus.ready
    assert embedding_service.calls
    assert fake_collection.upserts


def test_document_ingestion_fails_when_no_text_is_extracted(db_session, tmp_path):
    admin = _admin_user(db_session)
    embedding_service = _FakeEmbeddingService("openai", "text-embedding-3-small")
    service = DocumentIngestionService(db_session, embedding_service=embedding_service)
    service.settings.document_storage_dir = tmp_path
    fake_collection = _FakeCollection()
    service.vector_store._get_collection = lambda: fake_collection

    upload = _make_upload_file("empty.txt", b"", "text/plain")
    document = asyncio.run(service.save_upload(upload, "Empty File", admin))
    service.process_document(document.id)

    db_session.expire_all()
    stored_document = db_session.get(Document, document.id)
    assert stored_document is not None
    assert stored_document.status == DocumentStatus.failed
    assert stored_document.failure_reason == "No text content could be extracted from the document"
