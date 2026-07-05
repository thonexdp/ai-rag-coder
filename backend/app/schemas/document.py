from datetime import datetime

from pydantic import BaseModel

from app.database.models.document import DocumentStatus


class DocumentUploadResponse(BaseModel):
    document_id: int
    status: DocumentStatus


class DocumentRead(BaseModel):
    id: int
    title: str
    filename: str
    mime_type: str
    status: DocumentStatus
    failure_reason: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
