from datetime import datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.database.models import Announcement, Course, StudentSchedule, User, UserRole


def seed_initial_data(db: Session) -> None:
    admin = db.scalar(select(User).where(User.email == "admin@school.local"))
    if not admin:
        admin = User(
            email="admin@school.local",
            full_name="System Administrator",
            hashed_password=get_password_hash("Admin123!"),
            role=UserRole.admin,
        )
        db.add(admin)

    student = db.scalar(select(User).where(User.email == "student@school.local"))
    if not student:
        student = User(
            email="student@school.local",
            full_name="Demo Student",
            hashed_password=get_password_hash("Student123!"),
            role=UserRole.student,
        )
        db.add(student)
        db.flush()

    course = db.scalar(select(Course).where(Course.code == "CS101"))
    if not course:
        course = Course(code="CS101", title="Introduction to Computing", description="Fundamentals of computing")
        db.add(course)
        db.flush()

    existing_schedule = db.scalar(select(StudentSchedule).where(StudentSchedule.student_id == student.id))
    if not existing_schedule:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%A")
        db.add(
            StudentSchedule(
                student_id=student.id,
                course_id=course.id,
                weekday=tomorrow,
                start_time=time(hour=9, minute=0),
                end_time=time(hour=10, minute=30),
                room="Lab 2",
            )
        )

    existing_announcement = db.scalar(select(Announcement).where(Announcement.title == "Enrollment Week"))
    if not existing_announcement:
        db.add(
            Announcement(
                title="Enrollment Week",
                content="Enrollment starts next Monday at the registrar's office and online portal.",
            )
        )

    db.commit()
