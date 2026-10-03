from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.sos import SOSContact
from app.db.repositories.base import BaseRepository


class SOSRepository(BaseRepository[SOSContact]):
    def __init__(self, db: AsyncSession):
        super().__init__(SOSContact, db)

    async def get_active_contacts(
        self,
        category: Optional[str] = None,
        include_inactive: bool = False,
    ) -> List[SOSContact]:
        query = select(SOSContact)
        if not include_inactive:
            query = query.where(SOSContact.is_active.is_(True))
        if category:
            query = query.where(SOSContact.category == category.lower())
        query = query.order_by(SOSContact.priority.asc(), SOSContact.title.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
