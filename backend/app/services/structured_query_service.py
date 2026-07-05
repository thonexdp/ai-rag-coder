from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database.models import Announcement, Course, StudentSchedule, User
from app.schemas.academic import CourseScheduleRead


class StructuredQueryService:
    def __init__(self, db: Session):
        self.db = db

    def get_student_schedule(self, student: User, target_day: str | None = None) -> list[CourseScheduleRead]:
        weekday = target_day or (datetime.now() + timedelta(days=1)).strftime("%A")
        query = (
            select(StudentSchedule)
            .options(joinedload(StudentSchedule.course))
            .where(StudentSchedule.student_id == student.id, StudentSchedule.weekday == weekday)
            .order_by(StudentSchedule.start_time.asc())
        )
        schedules = self.db.scalars(query).all()
        return [
            CourseScheduleRead(
                id=item.id,
                weekday=item.weekday,
                start_time=item.start_time,
                end_time=item.end_time,
                room=item.room,
                course_code=item.course.code,
                course_title=item.course.title,
            )
            for item in schedules
        ]

    def get_announcements(self) -> list[Announcement]:
        return self.db.scalars(select(Announcement).order_by(Announcement.published_at.desc())).all()

    def get_courses(self) -> list[Course]:
        return self.db.scalars(select(Course).order_by(Course.code.asc())).all()

    def build_schedule_context(self, student: User) -> str:
        schedules = self.get_student_schedule(student)
        if not schedules:
            return "No schedule found for tomorrow."
        parts = [
            f"{item.course_code} {item.course_title} on {item.weekday} from {item.start_time} to {item.end_time}"
            + (f" in room {item.room}" if item.room else "")
            for item in schedules
        ]
        return "Tomorrow's classes: " + "; ".join(parts)

    def build_announcements_context(self) -> str:
        announcements = self.get_announcements()[:3]
        if not announcements:
            return "No announcements available."
        return "\n".join(f"{item.title}: {item.content}" for item in announcements)

    def build_courses_context(self) -> str:
        courses = self.get_courses()
        if not courses:
            return "No courses available."
        return "\n".join(
            f"{course.code}: {course.title}" + (f" - {course.description}" if course.description else "")
            for course in courses
        )
