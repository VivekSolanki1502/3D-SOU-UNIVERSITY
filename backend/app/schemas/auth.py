from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    display_name: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserBase(BaseModel):
    email: EmailStr
    display_name: str
    role: str = "student"
    department: Optional[str] = None
    is_active: bool = True


class UserCreate(BaseModel):
    email: EmailStr
    display_name: str
    department: Optional[str] = None
    password: str = Field(..., min_length=12)


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    role: Optional[Literal["visitor", "student", "faculty", "admin"]] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=12)


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
