from datetime import date, datetime, time

from pydantic import BaseModel, Field


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


class CourseRead(BaseModel):
    id: int
    code: str
    title: str
    description: str | None = None

    model_config = {"from_attributes": True}


class CourseCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    title: str = Field(min_length=2, max_length=255)
    description: str | None = None


class CourseUpdate(CourseCreate):
    pass


class StudentScheduleAdminRead(BaseModel):
    id: int
    student_id: int
    course_id: int
    weekday: str
    start_time: time
    end_time: time
    room: str | None = None
    student_name: str
    student_email: str
    course_code: str
    course_title: str


class StudentScheduleCreate(BaseModel):
    student_id: int
    course_id: int
    weekday: str = Field(min_length=2, max_length=16)
    start_time: time
    end_time: time
    room: str | None = Field(default=None, max_length=50)


class StudentScheduleUpdate(StudentScheduleCreate):
    pass


class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    content: str = Field(min_length=2)
    published_at: datetime | None = None


class AnnouncementUpdate(AnnouncementCreate):
    pass


class SchoolCalendarEventRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    event_date: date

    model_config = {"from_attributes": True}


class SchoolCalendarEventCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str | None = None
    event_date: date


class SchoolCalendarEventUpdate(SchoolCalendarEventCreate):
    pass
