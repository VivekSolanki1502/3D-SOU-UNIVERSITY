from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import cache_delete_pattern, cache_get, cache_set
from app.db.models.exam import Exam
from app.db.repositories.audit import AuditRepository
from app.db.repositories.exam import ExamRepository
from app.schemas.exam import ExamCreate, ExamUpdate


class ExamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ExamRepository(db)
        self.audit_repo = AuditRepository(db)

    async def get_exams(
        self,
        department: Optional[str] = None,
        semester: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Exam]:
        cache_key = f"exams:{department}:{semester}:{status}:{skip}:{limit}"
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached
        
        exams = await self.repo.get_exams(department, semester, status, skip, limit)
        return exams

    async def get_exam(self, exam_id: str) -> Optional[Exam]:
        return await self.repo.get_by_id(exam_id)

    async def create_exam(self, exam_in: ExamCreate, user_id: Optional[str] = None) -> Exam:
        data = exam_in.model_dump()
        data["created_by"] = user_id
        exam_obj = Exam(**data)
        created = await self.repo.create(exam_obj)
        await cache_delete_pattern("exams:*")
        
        await self.audit_repo.log_action(
            action="CREATE_EXAM",
            entity_type="exam",
            entity_id=created.id,
            actor_id=user_id,
            details=f"Created exam schedule for {created.subject_name} ({created.subject_code})"
        )
        return created

    async def update_exam(self, exam_id: str, exam_in: ExamUpdate, user_id: Optional[str] = None) -> Optional[Exam]:
        updated = await self.repo.update(exam_id, exam_in.model_dump(exclude_unset=True))
        await cache_delete_pattern("exams:*")
        if updated:
            await self.audit_repo.log_action(
                action="UPDATE_EXAM",
                entity_type="exam",
                entity_id=exam_id,
                actor_id=user_id,
                details=f"Updated exam schedule for {updated.subject_name}"
            )
        return updated

    async def delete_exam(self, exam_id: str, user_id: Optional[str] = None) -> bool:
        deleted = await self.repo.delete(exam_id)
        if deleted:
            await cache_delete_pattern("exams:*")
            await self.audit_repo.log_action(
                action="DELETE_EXAM",
                entity_type="exam",
                entity_id=exam_id,
                actor_id=user_id,
                details="Deleted exam schedule"
            )
        return deleted
