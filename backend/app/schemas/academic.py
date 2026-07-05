from datetime import datetime, time

from pydantic import BaseModel


class CourseScheduleRead(BaseModel):
    id: int
    weekday: str
    start_time: time
    end_time: time
    room: str | None
    course_code: str
    course_title: str


class AnnouncementRead(BaseModel):
    id: int
    title: str
    content: str
    published_at: datetime

    model_config = {"from_attributes": True}
