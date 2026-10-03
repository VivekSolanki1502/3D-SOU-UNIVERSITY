from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.exam import Exam
from app.db.repositories.base import BaseRepository


class ExamRepository(BaseRepository[Exam]):
    def __init__(self, db: AsyncSession):
        super().__init__(Exam, db)

    async def get_exams(
        self,
        department: Optional[str] = None,
        semester: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Exam]:
        query = select(Exam)
        if department:
            query = query.where(Exam.department.ilike(f"%{department.strip()}%"))
        if semester is not None:
            query = query.where(Exam.semester == semester)
        if status:
            query = query.where(Exam.status == status.lower())
        query = query.order_by(Exam.exam_date.asc(), Exam.start_time.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
