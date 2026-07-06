from app.api.v1 import chat as chat_api
from app.core.security import get_password_hash
from app.database.models import User, UserRole
from app.services.transcript_correction_service import TranscriptCorrectionService


def _student_token(client, db_session):
    student = User(
        email="student-voice@test.local",
        full_name="Student Voice",
        hashed_password=get_password_hash("StudentPass123"),
        role=UserRole.student,
    )
    db_session.add(student)
    db_session.commit()
    response = client.post("/api/v1/auth/login", json={"email": student.email, "password": "StudentPass123"})
    return response.json()["access_token"]


def test_transcript_correction_service_corrects_tagalog():
    service = TranscriptCorrectionService(
        text_generator=lambda messages, temperature: "Paano mag-login sa Flutter API?"
    )

    corrected = service.correct_transcript("pano mag login sa flutter api", "fil")

    assert corrected == "Paano mag-login sa Flutter API?"


def test_transcript_correction_service_returns_original_for_english():
    service = TranscriptCorrectionService(
        text_generator=lambda messages, temperature: "This should never be used"
    )

    corrected = service.correct_transcript("how to use Flutter API", "en")

    assert corrected == "how to use Flutter API"


def test_transcript_correction_service_returns_original_on_failure():
    def _raiser(messages, temperature):
        raise RuntimeError("provider unavailable")

    service = TranscriptCorrectionService(text_generator=_raiser)

    corrected = service.correct_transcript("unsaon pag gamit sa API", "ceb")

    assert corrected == "unsaon pag gamit sa API"


def test_transcript_correction_endpoint_returns_corrected_text(client, db_session, monkeypatch):
    class _FakeTranscriptCorrectionService:
        def correct_transcript(self, transcript: str, language: str | None) -> str:
            assert transcript == "pano mag login sa flutter api"
            assert language == "fil"
            return "Paano mag-login sa Flutter API?"

    monkeypatch.setattr(chat_api, "TranscriptCorrectionService", lambda: _FakeTranscriptCorrectionService())
    token = _student_token(client, db_session)

    response = client.post(
        "/api/v1/chat/transcript-correct",
        headers={"Authorization": f"Bearer {token}"},
        json={"transcript": "pano mag login sa flutter api", "language": "fil"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "corrected_transcript": "Paano mag-login sa Flutter API?",
        "language": "fil",
    }
