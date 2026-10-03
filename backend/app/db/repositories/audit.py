from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.audit import AuditLog
from app.db.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)

    async def log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        details: Optional[str] = None,
        metadata_json: Optional[dict] = None
    ) -> AuditLog:
        audit_obj = AuditLog(
            actor_id=actor_id,
            actor_email=actor_email,
            action=action.upper(),
            entity_type=entity_type.lower(),
            entity_id=entity_id,
            details=details,
            metadata_json=metadata_json or {}
        )
        return await self.create(audit_obj)

    async def get_logs(self, skip: int = 0, limit: int = 50) -> List[AuditLog]:
        query = select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
