from datetime import date, datetime, time
from typing import Optional
from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "academic"
    event_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    venue: str
    building_id: Optional[str] = None
    room_id: Optional[str] = None
    organizer: Optional[str] = None
    is_published: bool = True


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    event_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    venue: Optional[str] = None
    building_id: Optional[str] = None
    room_id: Optional[str] = None
    organizer: Optional[str] = None
    is_published: Optional[bool] = None


class EventResponse(EventBase):
    id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
