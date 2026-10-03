from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# Building Schemas
class BuildingBase(BaseModel):
    id: str
    name: str
    short_code: str
    department: Optional[str] = None
    faculty_lead: Optional[str] = None
    floors_count: int = 1
    pos_x: float = 0.0
    pos_z: float = 0.0
    dim_w: float = 4.0
    dim_d: float = 3.0
    dim_h: float = 4.0
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BaseModel):
    name: Optional[str] = None
    short_code: Optional[str] = None
    department: Optional[str] = None
    faculty_lead: Optional[str] = None
    floors_count: Optional[int] = None
    pos_x: Optional[float] = None
    pos_z: Optional[float] = None
    dim_w: Optional[float] = None
    dim_d: Optional[float] = None
    dim_h: Optional[float] = None
    description: Optional[str] = None
    aliases: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class BuildingResponse(BuildingBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Floor Schemas
class FloorBase(BaseModel):
    id: str
    building_id: str
    floor_number: int
    floor_label: str
    description: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class FloorCreate(FloorBase):
    pass


class FloorResponse(FloorBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Room Schemas
class RoomBase(BaseModel):
    id: str
    building_id: str
    floor_number: int = 0
    room_number: str
    name: str
    room_type: str
    department: Optional[str] = None
    faculty_in_charge: Optional[str] = None
    capacity: Optional[int] = None
    model_id: Optional[str] = None
    coordinates_3d: Dict[str, Any] = Field(default_factory=dict)
    aliases: List[str] = Field(default_factory=list)
    is_accessible: bool = True
    is_active: bool = True


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    building_id: Optional[str] = None
    floor_number: Optional[int] = None
    room_number: Optional[str] = None
    name: Optional[str] = None
    room_type: Optional[str] = None
    department: Optional[str] = None
    faculty_in_charge: Optional[str] = None
    capacity: Optional[int] = None
    model_id: Optional[str] = None
    coordinates_3d: Optional[Dict[str, Any]] = None
    aliases: Optional[List[str]] = None
    is_accessible: Optional[bool] = None
    is_active: Optional[bool] = None


class RoomResponse(RoomBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Facility Schemas
class FacilityBase(BaseModel):
    id: str
    name: str
    facility_type: str
    building_id: Optional[str] = None
    location_description: str
    code_symbol: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    is_accessible: bool = True
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class FacilityCreate(FacilityBase):
    pass


class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    facility_type: Optional[str] = None
    building_id: Optional[str] = None
    location_description: Optional[str] = None
    code_symbol: Optional[str] = None
    aliases: Optional[List[str]] = None
    is_accessible: Optional[bool] = None
    metadata_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class FacilityResponse(FacilityBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Search Result
class CampusSearchResult(BaseModel):
    id: str
    name: str
    category: str
    subtitle: str
    code: Optional[str] = None
    building_id: Optional[str] = None
    floor_number: Optional[int] = None
    model_id: Optional[str] = None
    coordinates_3d: Optional[Dict[str, Any]] = None
    is_accessible: bool = True
