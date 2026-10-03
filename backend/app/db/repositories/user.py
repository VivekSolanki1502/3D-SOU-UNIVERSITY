from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email.strip().lower()))
        return result.scalar_one_or_none()

    async def count_by_role(self) -> dict:
        result = await self.db.execute(select(User.role))
        roles = result.scalars().all()
        counts = {}
        for r in roles:
            counts[r] = counts.get(r, 0) + 1
        return counts
