from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.event import Event
from app.db.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self, db: AsyncSession):
        super().__init__(Event, db)

    async def get_published_events(
        self,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        include_unpublished: bool = False,
    ) -> List[Event]:
        query = select(Event)
        if not include_unpublished:
            query = query.where(Event.is_published.is_(True))
        if category:
            query = query.where(Event.category == category.lower())
        query = query.order_by(Event.event_date.asc(), Event.start_time.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
