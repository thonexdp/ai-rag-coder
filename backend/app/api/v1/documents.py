from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.database.database import get_db
from app.database.models import Document, User, UserRole
from app.schemas.document import DocumentRead, DocumentUploadResponse
from app.services.document_service import DocumentIngestionService


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    title: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
) -> DocumentUploadResponse:
    service = DocumentIngestionService(db)
    document = await service.save_upload(file, title, current_user)
    service.enqueue(background_tasks, document.id)
    return DocumentUploadResponse(document_id=document.id, status=document.status)


@router.get("", response_model=list[DocumentRead])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentRead]:
    documents = db.scalars(select(Document).order_by(Document.created_at.desc())).all()
    return [DocumentRead.model_validate(item) for item in documents]


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentRead.model_validate(document)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin)),
) -> None:
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    DocumentIngestionService(db).delete_document(document)
