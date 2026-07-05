from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.database.models import User
from app.schemas.academic import AnnouncementRead, CourseScheduleRead
from app.services.structured_query_service import StructuredQueryService


router = APIRouter(tags=["users"])


@router.get("/students/me/schedule", response_model=list[CourseScheduleRead])
def my_schedule(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CourseScheduleRead]:
    return StructuredQueryService(db).get_student_schedule(current_user)


@router.get("/announcements", response_model=list[AnnouncementRead])
def announcements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AnnouncementRead]:
    return [AnnouncementRead.model_validate(item) for item in StructuredQueryService(db).get_announcements()]
