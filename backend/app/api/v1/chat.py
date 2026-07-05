import json

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.database.models import User
from app.schemas.chat import ChatMessageRead, ChatRequest, ChatResponse, ChatSessionDetail, ChatSessionRead
from app.services.chat_service import ChatService


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    return ChatService(db).handle_chat(payload, current_user)


@router.get("/history", response_model=list[ChatSessionRead])
def list_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[ChatSessionRead]:
    sessions = ChatService(db).list_history(current_user)
    return [ChatSessionRead.model_validate(item) for item in sessions]


@router.get("/history/{session_id}", response_model=ChatSessionDetail)
def get_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatSessionDetail:
    try:
        session = ChatService(db).get_session_detail(session_id, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    messages = [
        ChatMessageRead(
            id=item.id,
            role=item.role,
            content=item.content,
            language=item.language,
            citations=[source for source in json.loads(item.citations_json or "[]")],
            created_at=item.created_at,
        )
        for item in session.messages
    ]
    return ChatSessionDetail(id=session.id, title=session.title, messages=messages)


@router.delete("/history/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    try:
        ChatService(db).delete_session(session_id, current_user)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
def delete_all_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    ChatService(db).delete_all_history(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
