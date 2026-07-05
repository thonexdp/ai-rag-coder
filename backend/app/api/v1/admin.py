from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth.dependencies import require_role
from app.core.security import get_password_hash
from app.database.database import get_db
from app.database.models import Announcement, Course, SchoolCalendarEvent, StudentSchedule, User, UserRole
from app.schemas.academic import (
    AnnouncementCreate,
    AnnouncementRead,
    AnnouncementUpdate,
    CourseCreate,
    CourseRead,
    CourseUpdate,
    SchoolCalendarEventCreate,
    SchoolCalendarEventRead,
    SchoolCalendarEventUpdate,
    StudentScheduleAdminRead,
    StudentScheduleCreate,
    StudentScheduleUpdate,
)
from app.schemas.auth import AdminUserCreate, AdminUserUpdate, UserRead


router = APIRouter(tags=["admin"])


def _admin_user(_: User = Depends(require_role(UserRole.admin))) -> User:
    return _


@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(_admin_user)) -> list[UserRead]:
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [UserRead.model_validate(user) for user in users]


@router.post("/users", response_model=UserRead)
def create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> UserRead:
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> UserRead:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = db.scalar(select(User).where(User.email == payload.email.lower(), User.id != user_id))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user.email = payload.email.lower()
    user.full_name = payload.full_name
    user.role = payload.role
    if payload.password:
        user.hashed_password = get_password_hash(payload.password)
    db.commit()
    db.refresh(user)
    return UserRead.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> Response:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own account")
    if user.schedules or user.documents or user.chat_sessions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User cannot be deleted while related schedules, documents, or chat history exist",
        )
    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/courses", response_model=list[CourseRead])
def list_courses(db: Session = Depends(get_db), current_user: User = Depends(_admin_user)) -> list[CourseRead]:
    courses = db.scalars(select(Course).order_by(Course.code.asc())).all()
    return [CourseRead.model_validate(course) for course in courses]


@router.post("/courses", response_model=CourseRead)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> CourseRead:
    existing = db.scalar(select(Course).where(Course.code == payload.code.strip().upper()))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course code already exists")

    course = Course(
        code=payload.code.strip().upper(),
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return CourseRead.model_validate(course)


@router.put("/courses/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int,
    payload: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> CourseRead:
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    existing = db.scalar(select(Course).where(Course.code == payload.code.strip().upper(), Course.id != course_id))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course code already exists")

    course.code = payload.code.strip().upper()
    course.title = payload.title.strip()
    course.description = payload.description.strip() if payload.description else None
    db.commit()
    db.refresh(course)
    return CourseRead.model_validate(course)


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> Response:
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.schedules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course cannot be deleted while schedules still reference it",
        )
    db.delete(course)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _schedule_read(item: StudentSchedule) -> StudentScheduleAdminRead:
    return StudentScheduleAdminRead(
        id=item.id,
        student_id=item.student_id,
        course_id=item.course_id,
        weekday=item.weekday,
        start_time=item.start_time,
        end_time=item.end_time,
        room=item.room,
        student_name=item.student.full_name,
        student_email=item.student.email,
        course_code=item.course.code,
        course_title=item.course.title,
    )


def _validate_schedule_relations(db: Session, payload: StudentScheduleCreate) -> tuple[User, Course]:
    student = db.get(User, payload.student_id)
    if not student or student.role != UserRole.student:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student not found")
    course = db.get(Course, payload.course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course not found")
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End time must be after start time")
    return student, course


@router.get("/schedules", response_model=list[StudentScheduleAdminRead])
def list_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> list[StudentScheduleAdminRead]:
    schedules = db.scalars(
        select(StudentSchedule)
        .options(selectinload(StudentSchedule.student), selectinload(StudentSchedule.course))
        .order_by(StudentSchedule.weekday.asc(), StudentSchedule.start_time.asc())
    ).all()
    return [_schedule_read(item) for item in schedules]


@router.post("/schedules", response_model=StudentScheduleAdminRead)
def create_schedule(
    payload: StudentScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> StudentScheduleAdminRead:
    _validate_schedule_relations(db, payload)
    schedule = StudentSchedule(
        student_id=payload.student_id,
        course_id=payload.course_id,
        weekday=payload.weekday.strip(),
        start_time=payload.start_time,
        end_time=payload.end_time,
        room=payload.room.strip() if payload.room else None,
    )
    db.add(schedule)
    db.commit()
    schedule = db.scalar(
        select(StudentSchedule)
        .options(selectinload(StudentSchedule.student), selectinload(StudentSchedule.course))
        .where(StudentSchedule.id == schedule.id)
    )
    return _schedule_read(schedule)


@router.put("/schedules/{schedule_id}", response_model=StudentScheduleAdminRead)
def update_schedule(
    schedule_id: int,
    payload: StudentScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> StudentScheduleAdminRead:
    schedule = db.get(StudentSchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    _validate_schedule_relations(db, payload)
    schedule.student_id = payload.student_id
    schedule.course_id = payload.course_id
    schedule.weekday = payload.weekday.strip()
    schedule.start_time = payload.start_time
    schedule.end_time = payload.end_time
    schedule.room = payload.room.strip() if payload.room else None
    db.commit()
    schedule = db.scalar(
        select(StudentSchedule)
        .options(selectinload(StudentSchedule.student), selectinload(StudentSchedule.course))
        .where(StudentSchedule.id == schedule.id)
    )
    return _schedule_read(schedule)


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> Response:
    schedule = db.get(StudentSchedule, schedule_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    db.delete(schedule)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/calendar", response_model=list[SchoolCalendarEventRead])
def list_calendar_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> list[SchoolCalendarEventRead]:
    events = db.scalars(select(SchoolCalendarEvent).order_by(SchoolCalendarEvent.event_date.asc())).all()
    return [SchoolCalendarEventRead.model_validate(item) for item in events]


@router.post("/calendar", response_model=SchoolCalendarEventRead)
def create_calendar_event(
    payload: SchoolCalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> SchoolCalendarEventRead:
    event = SchoolCalendarEvent(
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        event_date=payload.event_date,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return SchoolCalendarEventRead.model_validate(event)


@router.put("/calendar/{event_id}", response_model=SchoolCalendarEventRead)
def update_calendar_event(
    event_id: int,
    payload: SchoolCalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> SchoolCalendarEventRead:
    event = db.get(SchoolCalendarEvent, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found")
    event.title = payload.title.strip()
    event.description = payload.description.strip() if payload.description else None
    event.event_date = payload.event_date
    db.commit()
    db.refresh(event)
    return SchoolCalendarEventRead.model_validate(event)


@router.delete("/calendar/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> Response:
    event = db.get(SchoolCalendarEvent, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar event not found")
    db.delete(event)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/announcements", response_model=AnnouncementRead)
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> AnnouncementRead:
    announcement = Announcement(
        title=payload.title.strip(),
        content=payload.content.strip(),
        published_at=payload.published_at or datetime.utcnow(),
    )
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    return AnnouncementRead.model_validate(announcement)


@router.put("/announcements/{announcement_id}", response_model=AnnouncementRead)
def update_announcement(
    announcement_id: int,
    payload: AnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> AnnouncementRead:
    announcement = db.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")
    announcement.title = payload.title.strip()
    announcement.content = payload.content.strip()
    announcement.published_at = payload.published_at or announcement.published_at
    db.commit()
    db.refresh(announcement)
    return AnnouncementRead.model_validate(announcement)


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(_admin_user),
) -> Response:
    announcement = db.get(Announcement, announcement_id)
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found")
    db.delete(announcement)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
