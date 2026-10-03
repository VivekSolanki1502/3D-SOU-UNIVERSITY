from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import cache_delete_pattern, cache_get, cache_set
from app.db.models.sos import SOSContact
from app.db.repositories.sos import SOSRepository
from app.schemas.sos import SOSContactCreate, SOSContactUpdate


class SOSService:
    def __init__(self, db: AsyncSession):
        self.repo = SOSRepository(db)

    async def get_active_contacts(
        self,
        category: Optional[str] = None,
        include_inactive: bool = False,
    ) -> List[SOSContact]:
        visibility = "all" if include_inactive else "active"
        cache_key = f"sos:{visibility}:{category}"
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached
        
        contacts = await self.repo.get_active_contacts(category, include_inactive)
        return contacts

    async def get_contact(self, contact_id: str) -> Optional[SOSContact]:
        return await self.repo.get_by_id(contact_id)

    async def create_contact(self, contact_in: SOSContactCreate) -> SOSContact:
        contact_obj = SOSContact(**contact_in.model_dump())
        created = await self.repo.create(contact_obj)
        await cache_delete_pattern("sos:*")
        return created

    async def update_contact(self, contact_id: str, contact_in: SOSContactUpdate) -> Optional[SOSContact]:
        updated = await self.repo.update(contact_id, contact_in.model_dump(exclude_unset=True))
        await cache_delete_pattern("sos:*")
        return updated

    async def delete_contact(self, contact_id: str) -> bool:
        deleted = await self.repo.delete(contact_id)
        if deleted:
            await cache_delete_pattern("sos:*")
        return deleted
