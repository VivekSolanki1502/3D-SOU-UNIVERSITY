from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_admin, require_faculty_or_admin, require_student_or_above
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.exam import ExamCreate, ExamResponse, ExamUpdate
from app.services.exam import ExamService

router = APIRouter()


@router.get("", response_model=List[ExamResponse], summary="List published exams (Student/Faculty/Admin)")
async def list_exams(
    department: Optional[str] = Query(None, description="Department filter"),
    semester: Optional[int] = Query(None, description="Semester filter"),
    status_filter: Optional[str] = Query(None, alias="status", description="Exam status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_student_or_above),
    db: AsyncSession = Depends(get_db)
):
    service = ExamService(db)
    return await service.get_exams(
        department=department,
        semester=semester,
        status=status_filter,
        skip=skip,
        limit=limit
    )


@router.get("/{exam_id}", response_model=ExamResponse, summary="Get single exam schedule (Student/Faculty/Admin)")
async def get_exam(
    exam_id: str,
    current_user: User = Depends(require_student_or_above),
    db: AsyncSession = Depends(get_db)
):
    service = ExamService(db)
    exam = await service.get_exam(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam schedule not found")
    return exam


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED, summary="Create exam schedule (Faculty/Admin)")
async def create_exam(
    exam_in: ExamCreate,
    current_user: User = Depends(require_faculty_or_admin),
    db: AsyncSession = Depends(get_db)
):
    service = ExamService(db)
    return await service.create_exam(exam_in, user_id=current_user.id)


@router.patch("/{exam_id}", response_model=ExamResponse, summary="Update exam schedule (Faculty/Admin)")
async def update_exam(
    exam_id: str,
    exam_in: ExamUpdate,
    current_user: User = Depends(require_faculty_or_admin),
    db: AsyncSession = Depends(get_db)
):
    service = ExamService(db)
    updated = await service.update_exam(exam_id, exam_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Exam schedule not found")
    return updated


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete exam schedule (Admin only)")
async def delete_exam(
    exam_id: str,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = ExamService(db)
    deleted = await service.delete_exam(exam_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exam schedule not found")
