from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import cache_delete_pattern, cache_get, cache_set
from app.db.models.event import Event
from app.db.repositories.event import EventRepository
from app.schemas.event import EventCreate, EventUpdate


class EventService:
    def __init__(self, db: AsyncSession):
        self.repo = EventRepository(db)

    async def get_published_events(
        self,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        include_unpublished: bool = False,
    ) -> List[Event]:
        visibility = "all" if include_unpublished else "published"
        cache_key = f"events:{visibility}:{category}:{skip}:{limit}"
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached
        
        events = await self.repo.get_published_events(category, skip, limit, include_unpublished)
        return events

    async def get_event(self, event_id: str) -> Optional[Event]:
        return await self.repo.get_by_id(event_id)

    async def create_event(self, event_in: EventCreate, user_id: Optional[str] = None) -> Event:
        data = event_in.model_dump()
        data["created_by"] = user_id
        event_obj = Event(**data)
        created = await self.repo.create(event_obj)
        await cache_delete_pattern("events:*")
        return created

    async def update_event(self, event_id: str, event_in: EventUpdate) -> Optional[Event]:
        updated = await self.repo.update(event_id, event_in.model_dump(exclude_unset=True))
        await cache_delete_pattern("events:*")
        return updated

    async def delete_event(self, event_id: str) -> bool:
        deleted = await self.repo.delete(event_id)
        if deleted:
            await cache_delete_pattern("events:*")
        return deleted
