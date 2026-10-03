from datetime import date, datetime, time
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ExamBase(BaseModel):
    subject_name: str
    subject_code: str
    course: str
    department: str
    semester: int
    exam_date: date
    start_time: time
    end_time: time
    venue: str
    building_id: Optional[str] = None
    room_id: Optional[str] = None
    status: str = "scheduled"
    description: Optional[str] = None


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    course: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = None
    exam_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    venue: Optional[str] = None
    building_id: Optional[str] = None
    room_id: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None


class ExamResponse(ExamBase):
    id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
