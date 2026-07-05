from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter

import docx2txt
from fastapi import BackgroundTasks, HTTPException, UploadFile, status
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.database import SessionLocal
from app.database.models import Document, DocumentStatus, User
from app.rag.chunking import split_text
from app.services.embedding_service import get_embedding_service
from app.services.interfaces import EmbeddingService
from app.services.vector_store import ChromaVectorStoreService
from app.utils.file_utils import build_storage_filename
from app.utils.language import detect_language


logger = logging.getLogger(__name__)


class DocumentIngestionService:
    def __init__(
        self,
        db: Session,
        vector_store: ChromaVectorStoreService | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.db = db
        self.settings = get_settings()
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_store = vector_store or ChromaVectorStoreService(self.embedding_service)

    async def save_upload(self, upload: UploadFile, title: str | None, current_user: User) -> Document:
        filename = upload.filename or "document.txt"
        suffix = Path(filename).suffix.lower()
        if suffix not in self.settings.allowed_upload_extensions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file extension")
        if upload.content_type not in self.settings.allowed_upload_mime_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

        content = await upload.read()
        if len(content) > self.settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File exceeds upload limit")

        storage_name = build_storage_filename(filename)
        storage_path = self.settings.document_storage_dir / storage_name
        storage_path.write_bytes(content)

        document = Document(
            title=title or Path(filename).stem,
            filename=storage_name,
            mime_type=upload.content_type,
            uploaded_by=current_user.id,
            storage_path=str(storage_path),
            status=DocumentStatus.pending,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        logger.info(
            "Document upload saved: document_id=%s filename=%s size_bytes=%s mime_type=%s",
            document.id,
            filename,
            len(content),
            upload.content_type,
        )
        return document

    def enqueue(self, background_tasks: BackgroundTasks, document_id: int) -> None:
        background_tasks.add_task(self.process_document, document_id)

    def process_document(self, document_id: int) -> None:
        db = SessionLocal()
        started_at = perf_counter()
        try:
            document = db.get(Document, document_id)
            if not document:
                return
            document.status = DocumentStatus.processing
            document.failure_reason = None
            db.commit()
            logger.info(
                "Document ingestion started: document_id=%s path=%s provider=%s model=%s collection=%s",
                document.id,
                document.storage_path,
                self.embedding_service.provider_name,
                self.embedding_service.model_name,
                self.vector_store.collection_name,
            )

            extraction_started_at = perf_counter()
            raw_text = self._extract_text(Path(document.storage_path))
            logger.info(
                "Document text extracted: document_id=%s characters=%s extraction_seconds=%.2f",
                document.id,
                len(raw_text),
                perf_counter() - extraction_started_at,
            )

            chunking_started_at = perf_counter()
            chunks = split_text(raw_text)
            logger.info(
                "Document chunking complete: document_id=%s chunks=%s chunking_seconds=%.2f",
                document.id,
                len(chunks),
                perf_counter() - chunking_started_at,
            )
            vector_payload = []
            for index, chunk in enumerate(chunks):
                vector_payload.append(
                    {
                        "id": f"document-{document.id}-chunk-{index}",
                        "content": chunk,
                        "metadata": {
                            "document_id": document.id,
                            "title": document.title,
                            "source_type": "document",
                            "chunk_index": index,
                            "language": detect_language(chunk),
                        },
                    }
                )

            if not vector_payload:
                raise ValueError("No text content could be extracted from the document")

            logger.info("Document embedding/upsert starting: document_id=%s chunks=%s", document.id, len(vector_payload))
            self.vector_store.upsert_chunks(vector_payload)
            document.status = DocumentStatus.ready
            db.commit()
            logger.info(
                "Document ingestion completed: document_id=%s total_seconds=%.2f",
                document.id,
                perf_counter() - started_at,
            )
        except Exception as exc:  # pragma: no cover - background execution
            logger.exception("Document ingestion failed: document_id=%s", document_id)
            document = db.get(Document, document_id)
            if document:
                document.status = DocumentStatus.failed
                document.failure_reason = str(exc)
                db.commit()
        finally:
            db.close()

    def delete_document(self, document: Document) -> None:
        self.vector_store.delete_document(document.id)
        path = Path(document.storage_path)
        if path.exists():
            path.unlink()
        self.db.delete(document)
        self.db.commit()

    def _extract_text(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".pdf":
            reader = PdfReader(str(path))
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        if suffix == ".docx":
            return docx2txt.process(str(path))
        raise ValueError("Unsupported file type during extraction")
