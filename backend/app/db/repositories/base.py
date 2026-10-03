from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, id: Any, update_data: dict) -> Optional[ModelType]:
        clean_data = {k: v for k, v in update_data.items() if v is not None}
        if not clean_data:
            return await self.get_by_id(id)
        
        await self.db.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**clean_data)
        )
        await self.db.flush()
        return await self.get_by_id(id)

    async def delete(self, id: Any) -> bool:
        result = await self.db.execute(delete(self.model).where(self.model.id == id))
        await self.db.flush()
        return result.rowcount > 0
