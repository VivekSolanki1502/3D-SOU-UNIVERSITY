from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.models.user import User
from app.db.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, Token, UserCreate


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def authenticate(self, login_data: LoginRequest) -> Token:
        user = await self.user_repo.get_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user account",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_str = create_access_token(subject=user.id, role=user.role)
        return Token(
            access_token=token_str,
            token_type="bearer",
            role=user.role,
            user_id=user.id,
            display_name=user.display_name
        )

    async def register(self, user_in: UserCreate) -> User:
        existing = await self.user_repo.get_by_email(user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        user_obj = User(
            email=user_in.email.strip().lower(),
            hashed_password=get_password_hash(user_in.password),
            display_name=user_in.display_name.strip(),
            role="student",
            department=user_in.department,
            is_active=True
        )
        return await self.user_repo.create(user_obj)
