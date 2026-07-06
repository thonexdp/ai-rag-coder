from datetime import datetime

from pydantic import BaseModel, Field


class ChatSource(BaseModel):
    document_id: int | None = None
    title: str
    snippet: str
    page: int | None = None
    source_type: str = "document"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    session_id: int | None = None
    language: str | None = Field(default=None, max_length=20)


class TranscriptCorrectionRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=4000)
    language: str | None = Field(default=None, max_length=20)


class TranscriptCorrectionResponse(BaseModel):
    corrected_transcript: str
    language: str


class ChatResponse(BaseModel):
    answer: str
    language: str
    session_id: int
    sources: list[ChatSource]
    mode: str


class ChatMessageRead(BaseModel):
    id: int
    role: str
    content: str
    language: str
    citations: list[ChatSource] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionRead(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionDetail(BaseModel):
    id: int
    title: str
    messages: list[ChatMessageRead]

    model_config = {"from_attributes": True}
