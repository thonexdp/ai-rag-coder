from __future__ import annotations

import json
import logging
from time import perf_counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import ChatMessage, ChatSession, User
from app.rag.prompt_builder import build_prompt
from app.rag.retriever import Retriever
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services.interfaces import LLMService
from app.services.llm_service import get_llm_service
from app.services.structured_query_service import StructuredQueryService
from app.services.vector_store import ChromaVectorStoreService
from app.utils.language import detect_language


logger = logging.getLogger(__name__)


class ChatService:
    _smalltalk_tokens = {
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "kumusta",
        "kamusta",
        "yo",
    }

    def __init__(
        self,
        db: Session,
        llm_service: LLMService | None = None,
        vector_store: ChromaVectorStoreService | None = None,
    ) -> None:
        self.db = db
        self.llm_service = llm_service or get_llm_service()
        self.vector_store = vector_store or ChromaVectorStoreService()
        self.retriever = Retriever(self.vector_store)
        self.structured_service = StructuredQueryService(db)

    def handle_chat(self, payload: ChatRequest, current_user: User) -> ChatResponse:
        started_at = perf_counter()
        language = detect_language(payload.message, payload.language)
        session = self._get_or_create_session(payload.session_id, current_user, payload.message)
        mode = self._classify_mode(payload.message)
        normalized = " ".join(payload.message.lower().split())

        sources: list[ChatSource] = []
        structured_context = None
        retrieval_seconds = 0.0
        llm_seconds = 0.0
        if mode == "smalltalk":
            answer = self._smalltalk_answer(language)
        elif mode == "structured_data":
            answer = self._structured_answer(normalized, current_user, language)
        else:
            if mode in {"document_rag", "hybrid"}:
                retrieval_started_at = perf_counter()
                sources = self.retriever.search(payload.message)
                retrieval_seconds = perf_counter() - retrieval_started_at
            if mode in {"structured_data", "hybrid"}:
                structured_context = self._build_structured_context(normalized, current_user)

            if not sources and not structured_context:
                answer = self._fallback_answer(language)
            else:
                memory = self._load_memory(session.id)
                prompt = build_prompt(payload.message, language, sources, structured_context, memory)
                llm_started_at = perf_counter()
                answer = self.llm_service.generate_answer(prompt, language)
                llm_seconds = perf_counter() - llm_started_at

        self._persist_message(session.id, "user", payload.message, language, [])
        self._persist_message(session.id, "assistant", answer, language, sources)
        logger.info(
            "Chat handled: mode=%s provider=%s sources=%s retrieval_seconds=%.2f llm_seconds=%.2f total_seconds=%.2f",
            mode,
            self.llm_service.__class__.__name__,
            len(sources),
            retrieval_seconds,
            llm_seconds,
            perf_counter() - started_at,
        )
        return ChatResponse(answer=answer, language=language, session_id=session.id, sources=sources, mode=mode)

    def list_history(self, current_user: User) -> list[ChatSession]:
        query = select(ChatSession).where(ChatSession.user_id == current_user.id).order_by(ChatSession.updated_at.desc())
        return self.db.scalars(query).all()

    def get_session_detail(self, session_id: int, current_user: User) -> ChatSession:
        session = self.db.get(ChatSession, session_id)
        if not session or session.user_id != current_user.id:
            raise ValueError("Chat session not found")
        return session

    def delete_session(self, session_id: int, current_user: User) -> None:
        session = self.db.get(ChatSession, session_id)
        if not session or session.user_id != current_user.id:
            raise ValueError("Chat session not found")
        self.db.delete(session)
        self.db.commit()

    def delete_all_history(self, current_user: User) -> None:
        query = select(ChatSession).where(ChatSession.user_id == current_user.id)
        sessions = self.db.scalars(query).all()
        for session in sessions:
            self.db.delete(session)
        self.db.commit()

    def _classify_mode(self, message: str) -> str:
        normalized = " ".join(message.lower().split())
        if normalized in self._smalltalk_tokens:
            return "smalltalk"

        mentions_schedule = any(token in normalized for token in ("subjects", "schedule", "tomorrow", "klase"))
        mentions_announcement = "announcement" in normalized
        mentions_courses = any(token in normalized for token in ("course", "courses", "subject available", "available subjects"))
        mentions_docs = any(token in normalized for token in ("summarize", "chapter", "policy", "scholarship", "enrollment"))

        if (mentions_schedule or mentions_announcement or mentions_courses) and mentions_docs:
            return "hybrid"
        if mentions_schedule or mentions_announcement or mentions_courses:
            return "structured_data"
        return "document_rag"

    def _build_structured_context(self, normalized: str, current_user: User) -> str:
        contexts: list[str] = []
        if any(token in normalized for token in ("subjects", "schedule", "tomorrow", "klase")):
            contexts.append(self.structured_service.build_schedule_context(current_user))
        if "announcement" in normalized:
            contexts.append(self.structured_service.build_announcements_context())
        if any(token in normalized for token in ("course", "courses", "subject available", "available subjects")):
            contexts.append(self.structured_service.build_courses_context())
        return "\n".join(contexts)

    def _get_or_create_session(self, session_id: int | None, current_user: User, message: str) -> ChatSession:
        if session_id is not None:
            session = self.db.get(ChatSession, session_id)
            if session and session.user_id == current_user.id:
                return session
        session = ChatSession(user_id=current_user.id, title=message[:60])
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def _persist_message(
        self, session_id: int, role: str, content: str, language: str, sources: list[ChatSource]
    ) -> None:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            language=language,
            citations_json=json.dumps([source.model_dump() for source in sources]),
        )
        self.db.add(message)
        self.db.commit()

    def _load_memory(self, session_id: int) -> list[str]:
        query = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(6)
        )
        messages = list(reversed(self.db.scalars(query).all()))
        return [f"{item.role}: {item.content}" for item in messages]

    def _smalltalk_answer(self, language: str) -> str:
        if language == "fil":
            return "Hello. Maaari kang magtanong tungkol sa iskedyul, announcements, policies, o uploaded school documents."
        if language == "ceb":
            return "Hello. Pwede ka mangutana bahin sa schedule, announcements, policies, o uploaded school documents."
        return "Hello. You can ask me about schedules, announcements, policies, or uploaded school documents."

    def _structured_answer(self, normalized: str, current_user: User, language: str) -> str:
        if any(token in normalized for token in ("subjects", "schedule", "tomorrow", "klase")):
            context = self.structured_service.build_schedule_context(current_user)
            if language == "fil":
                return f"Ito ang iskedyul mo: {context}"
            if language == "ceb":
                return f"Mao ni ang imong iskedyul: {context}"
            return context

        if "announcement" in normalized:
            context = self.structured_service.build_announcements_context()
            if language == "fil":
                return f"Naritong mga announcement: {context}"
            if language == "ceb":
                return f"Aniay mga announcement: {context}"
            return f"Here are the latest announcements: {context}"

        if any(token in normalized for token in ("course", "courses", "subject available", "available subjects")):
            context = self.structured_service.build_courses_context()
            if language == "fil":
                return f"Ito ang mga available na course: {context}"
            if language == "ceb":
                return f"Mao ni ang mga available nga kurso: {context}"
            return f"Here are the available courses: {context}"

        return self._fallback_answer(language)

    def _fallback_answer(self, language: str) -> str:
        if language == "fil":
            return "Wala pa akong sapat na local context para masagot iyan nang tama."
        if language == "ceb":
            return "Wala pa koy igo nga local context aron matubag kana og sakto."
        return "I do not have enough local context yet to answer that reliably."
