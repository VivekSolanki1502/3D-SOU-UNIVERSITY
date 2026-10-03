from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import get_current_user
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import LoginRequest, Token, UserCreate, UserResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/login", response_model=Token, summary="User login with email & password")
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.authenticate(login_data)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register user account")
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.register(user_in)


@router.get("/me", response_model=UserResponse, summary="Get current authenticated user profile")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
