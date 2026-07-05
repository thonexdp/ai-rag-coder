from datetime import date

from app.core.security import get_password_hash
from app.database.models import Announcement, Course, SchoolCalendarEvent, StudentSchedule, User, UserRole


def _admin_token(client, db_session) -> str:
    admin = User(
        email="admin-admin@test.local",
        full_name="Admin User",
        hashed_password=get_password_hash("AdminPass123"),
        role=UserRole.admin,
    )
    db_session.add(admin)
    db_session.commit()
    response = client.post("/api/v1/auth/login", json={"email": admin.email, "password": "AdminPass123"})
    return response.json()["access_token"]


def _student(db_session) -> User:
    student = User(
        email="student-admin@test.local",
        full_name="Student Admin Test",
        hashed_password=get_password_hash("StudentPass123"),
        role=UserRole.student,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


def _course(db_session) -> Course:
    course = Course(code="CS201", title="Data Structures", description="Core CS course")
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


def test_admin_user_crud(client, db_session):
    token = _admin_token(client, db_session)
    create = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "faculty@test.local",
            "full_name": "Faculty Test",
            "password": "FacultyPass123",
            "role": "faculty",
        },
    )
    assert create.status_code == 200
    created = create.json()
    assert created["role"] == "faculty"

    listing = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert listing.status_code == 200
    assert any(item["email"] == "faculty@test.local" for item in listing.json())

    update = client.put(
        f"/api/v1/users/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "faculty-updated@test.local",
            "full_name": "Faculty Updated",
            "role": "admin",
            "password": "UpdatedPass123",
        },
    )
    assert update.status_code == 200
    assert update.json()["email"] == "faculty-updated@test.local"

    delete = client.delete(f"/api/v1/users/{created['id']}", headers={"Authorization": f"Bearer {token}"})
    assert delete.status_code == 204


def test_non_admin_cannot_access_admin_routes(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "student-only@test.local",
            "full_name": "Student Only",
            "password": "StudentPass123",
            "role": "student",
        },
    )
    login = client.post("/api/v1/auth/login", json={"email": "student-only@test.local", "password": "StudentPass123"})
    token = login.json()["access_token"]
    response = client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_course_crud(client, db_session):
    token = _admin_token(client, db_session)
    create = client.post(
        "/api/v1/courses",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "it101", "title": "Intro to IT", "description": "Basics"},
    )
    assert create.status_code == 200
    created = create.json()
    assert created["code"] == "IT101"

    update = client.put(
        f"/api/v1/courses/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"code": "IT102", "title": "Updated IT", "description": "Updated"},
    )
    assert update.status_code == 200
    assert update.json()["code"] == "IT102"

    delete = client.delete(f"/api/v1/courses/{created['id']}", headers={"Authorization": f"Bearer {token}"})
    assert delete.status_code == 204


def test_admin_schedule_crud(client, db_session):
    token = _admin_token(client, db_session)
    student = _student(db_session)
    course = _course(db_session)
    create = client.post(
        "/api/v1/schedules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "student_id": student.id,
            "course_id": course.id,
            "weekday": "Monday",
            "start_time": "08:00:00",
            "end_time": "09:30:00",
            "room": "Room 2",
        },
    )
    assert create.status_code == 200
    created = create.json()
    assert created["student_email"] == student.email
    assert created["course_code"] == course.code

    update = client.put(
        f"/api/v1/schedules/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "student_id": student.id,
            "course_id": course.id,
            "weekday": "Tuesday",
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "room": "Room 5",
        },
    )
    assert update.status_code == 200
    assert update.json()["weekday"] == "Tuesday"

    delete = client.delete(f"/api/v1/schedules/{created['id']}", headers={"Authorization": f"Bearer {token}"})
    assert delete.status_code == 204


def test_admin_calendar_crud(client, db_session):
    token = _admin_token(client, db_session)
    create = client.post(
        "/api/v1/calendar",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Orientation", "description": "New student orientation", "event_date": "2026-08-15"},
    )
    assert create.status_code == 200
    created = create.json()

    listing = client.get("/api/v1/calendar", headers={"Authorization": f"Bearer {token}"})
    assert listing.status_code == 200
    assert any(item["title"] == "Orientation" for item in listing.json())

    update = client.put(
        f"/api/v1/calendar/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Orientation Day", "description": "Updated", "event_date": "2026-08-16"},
    )
    assert update.status_code == 200
    assert update.json()["event_date"] == "2026-08-16"

    delete = client.delete(f"/api/v1/calendar/{created['id']}", headers={"Authorization": f"Bearer {token}"})
    assert delete.status_code == 204


def test_admin_announcement_crud(client, db_session):
    token = _admin_token(client, db_session)
    create = client.post(
        "/api/v1/announcements",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Enrollment", "content": "Enrollment opens Monday."},
    )
    assert create.status_code == 200
    created = create.json()

    update = client.put(
        f"/api/v1/announcements/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Enrollment Week", "content": "Enrollment opens Tuesday."},
    )
    assert update.status_code == 200
    assert update.json()["title"] == "Enrollment Week"

    delete = client.delete(f"/api/v1/announcements/{created['id']}", headers={"Authorization": f"Bearer {token}"})
    assert delete.status_code == 204


def test_schedule_validation_rejects_missing_student(client, db_session):
    token = _admin_token(client, db_session)
    course = _course(db_session)
    response = client.post(
        "/api/v1/schedules",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "student_id": 999,
            "course_id": course.id,
            "weekday": "Monday",
            "start_time": "08:00:00",
            "end_time": "09:30:00",
        },
    )
    assert response.status_code == 400


def test_user_delete_self_is_blocked(client, db_session):
    token = _admin_token(client, db_session)
    admin = db_session.query(User).filter(User.email == "admin-admin@test.local").one()
    response = client.delete(f"/api/v1/users/{admin.id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
