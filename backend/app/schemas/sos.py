from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class SOSContactBase(BaseModel):
    title: str
    category: str = "security"
    phone_number: str
    alternate_phone: Optional[str] = None
    location_name: str
    building_id: Optional[str] = None
    room_id: Optional[str] = None
    coordinates_3d: Dict[str, Any] = Field(default_factory=dict)
    available_hours: str = "24/7"
    priority: int = 1
    description: Optional[str] = None
    is_active: bool = True


class SOSContactCreate(SOSContactBase):
    pass


class SOSContactUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    phone_number: Optional[str] = None
    alternate_phone: Optional[str] = None
    location_name: Optional[str] = None
    building_id: Optional[str] = None
    room_id: Optional[str] = None
    coordinates_3d: Optional[Dict[str, Any]] = None
    available_hours: Optional[str] = None
    priority: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SOSContactResponse(SOSContactBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
