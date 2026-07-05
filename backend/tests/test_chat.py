from datetime import datetime, time, timedelta

from app.core.security import get_password_hash
from app.database.models import Announcement, Course, StudentSchedule, User, UserRole
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.services.interfaces import LLMService


class _GuardLLMService(LLMService):
    def generate_answer(self, prompt: str, language: str) -> str:  # pragma: no cover - should never run
        raise AssertionError("Structured-only questions should not call the LLM")


class _GuardVectorStore:
    def upsert_chunks(self, chunks):
        raise AssertionError("Structured-only questions should not write to the vector store")

    def chunk_search(self, query, limit=4):  # pragma: no cover - should never run
        raise AssertionError("Structured-only questions should not perform vector search")

    def delete_document(self, document_id):
        raise AssertionError("Structured-only questions should not delete from the vector store")


def _student_token(client, db_session):
    student = User(
        email="student@test.local",
        full_name="Student Test",
        hashed_password=get_password_hash("StudentPass123"),
        role=UserRole.student,
    )
    db_session.add(student)
    db_session.flush()
    course = Course(code="MATH101", title="College Algebra")
    db_session.add(course)
    db_session.flush()
    db_session.add(
        StudentSchedule(
            student_id=student.id,
            course_id=course.id,
            weekday=(datetime.now() + timedelta(days=1)).strftime("%A"),
            start_time=time(hour=8),
            end_time=time(hour=9, minute=30),
            room="Room 1",
        )
    )
    db_session.add(Announcement(title="Enrollment", content="Enrollment opens tomorrow."))
    db_session.commit()
    response = client.post("/api/v1/auth/login", json={"email": student.email, "password": "StudentPass123"})
    return response.json()["access_token"]


def test_chat_structured_schedule_answer(client, db_session):
    token = _student_token(client, db_session)
    response = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "What subjects do I have tomorrow?"},
    )
    assert response.status_code == 200
    assert response.json()["session_id"]
    assert response.json()["mode"] in {"structured_data", "hybrid"}


def test_chat_history_round_trip(client, db_session):
    token = _student_token(client, db_session)
    chat = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Any announcement today?"},
    )
    session_id = chat.json()["session_id"]

    history = client.get("/api/v1/chat/history", headers={"Authorization": f"Bearer {token}"})
    assert history.status_code == 200
    assert len(history.json()) >= 1

    detail = client.get(f"/api/v1/chat/history/{session_id}", headers={"Authorization": f"Bearer {token}"})
    assert detail.status_code == 200
    assert len(detail.json()["messages"]) == 2


def test_delete_single_chat_session(client, db_session):
    token = _student_token(client, db_session)
    chat = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Any announcement today?"},
    )
    session_id = chat.json()["session_id"]

    response = client.delete(f"/api/v1/chat/history/{session_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    history = client.get("/api/v1/chat/history", headers={"Authorization": f"Bearer {token}"})
    assert all(item["id"] != session_id for item in history.json())


def test_delete_other_users_chat_session_returns_404(client, db_session):
    owner_token = _student_token(client, db_session)
    chat = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"message": "Any announcement today?"},
    )
    session_id = chat.json()["session_id"]

    other_user = User(
        email="student-other@test.local",
        full_name="Other Student",
        hashed_password=get_password_hash("StudentPass123"),
        role=UserRole.student,
    )
    db_session.add(other_user)
    db_session.commit()

    other_login = client.post(
        "/api/v1/auth/login",
        json={"email": other_user.email, "password": "StudentPass123"},
    )
    other_token = other_login.json()["access_token"]

    response = client.delete(f"/api/v1/chat/history/{session_id}", headers={"Authorization": f"Bearer {other_token}"})
    assert response.status_code == 404


def test_delete_all_chat_history_only_removes_current_users_sessions(client, db_session):
    token = _student_token(client, db_session)
    client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Any announcement today?"},
    )

    other_user = User(
        email="student-history@test.local",
        full_name="History Student",
        hashed_password=get_password_hash("StudentPass123"),
        role=UserRole.student,
    )
    db_session.add(other_user)
    db_session.commit()

    other_login = client.post(
        "/api/v1/auth/login",
        json={"email": other_user.email, "password": "StudentPass123"},
    )
    other_token = other_login.json()["access_token"]
    client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"message": "hello"},
    )

    response = client.delete("/api/v1/chat/history", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204

    owner_history = client.get("/api/v1/chat/history", headers={"Authorization": f"Bearer {token}"})
    other_history = client.get("/api/v1/chat/history", headers={"Authorization": f"Bearer {other_token}"})
    assert owner_history.json() == []
    assert len(other_history.json()) == 1


def test_chat_announcements_uses_structured_fast_path(client, db_session):
    token = _student_token(client, db_session)
    response = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "What is announcements?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "structured_data"
    assert "announcement" in body["answer"].lower()


def test_chat_courses_uses_structured_fast_path(client, db_session):
    token = _student_token(client, db_session)
    response = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "what course available?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "structured_data"
    assert "course" in body["answer"].lower()


def test_chat_announcements_bypass_llm_and_vector_search(db_session):
    student = User(
        email="student-bypass@test.local",
        full_name="Student Test",
        hashed_password=get_password_hash("StudentPass123"),
        role=UserRole.student,
    )
    db_session.add(student)
    db_session.add(Announcement(title="Enrollment", content="Enrollment opens tomorrow."))
    db_session.commit()

    service = ChatService(
        db_session,
        llm_service=_GuardLLMService(),
        vector_store=_GuardVectorStore(),
    )
    response = service.handle_chat(ChatRequest(message="What are announcements?"), student)

    assert response.mode == "structured_data"
    assert "announcement" in response.answer.lower()
