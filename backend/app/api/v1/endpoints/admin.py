from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_admin
from app.core.security import get_password_hash
from app.db.models.campus import Building, Facility, Room
from app.db.models.event import Event
from app.db.models.exam import Exam
from app.db.models.sos import SOSContact
from app.db.models.user import User
from app.db.repositories.audit import AuditRepository
from app.db.repositories.user import UserRepository
from app.db.session import get_db
from app.schemas.audit import AuditLogResponse
from app.schemas.auth import UserResponse, UserUpdate

router = APIRouter()


@router.get("/stats", summary="Get Admin Dashboard overview metrics (Admin only)")
async def get_dashboard_stats(
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    buildings_count = (await db.execute(select(func.count(Building.id)))).scalar_one()
    rooms_count = (await db.execute(select(func.count(Room.id)))).scalar_one()
    facilities_count = (await db.execute(select(func.count(Facility.id)))).scalar_one()
    events_count = (await db.execute(select(func.count(Event.id)))).scalar_one()
    exams_count = (await db.execute(select(func.count(Exam.id)))).scalar_one()
    sos_count = (await db.execute(select(func.count(SOSContact.id)))).scalar_one()
    users_count = (await db.execute(select(func.count(User.id)))).scalar_one()

    user_repo = UserRepository(db)
    roles_distribution = await user_repo.count_by_role()

    return {
        "buildings": buildings_count,
        "rooms": rooms_count,
        "facilities": facilities_count,
        "events": events_count,
        "exams": exams_count,
        "sos_contacts": sos_count,
        "users": users_count,
        "role_distribution": roles_distribution
    }


@router.get("/users", response_model=List[UserResponse], summary="List all registered users (Admin only)")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    return await user_repo.get_all(skip=skip, limit=limit)


@router.patch("/users/{user_id}", response_model=UserResponse, summary="Update user status or role (Admin only)")
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.model_dump(exclude_unset=True)
    password = update_data.pop("password", None)
    if password is not None:
        update_data["hashed_password"] = get_password_hash(password)
    if user_id == current_admin.id and (
        update_data.get("is_active") is False
        or update_data.get("role", user.role).lower() != "admin"
    ):
        raise HTTPException(status_code=400, detail="Cannot disable or demote your own admin account")

    updated = await user_repo.update(user_id, update_data)
    
    audit_repo = AuditRepository(db)
    await audit_repo.log_action(
        action="UPDATE_USER",
        entity_type="user",
        entity_id=user_id,
        actor_id=current_admin.id,
        actor_email=current_admin.email,
        details=f"Updated user {user.email} (Role: {user_in.role or user.role})"
    )
    return updated


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user account (Admin only)")
async def delete_user(
    user_id: str,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    deleted = await user_repo.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    
    audit_repo = AuditRepository(db)
    await audit_repo.log_action(
        action="DELETE_USER",
        entity_type="user",
        entity_id=user_id,
        actor_id=current_admin.id,
        actor_email=current_admin.email,
        details=f"Deleted user account {user.email}"
    )


@router.get("/audit-logs", response_model=List[AuditLogResponse], summary="List security and admin audit logs (Admin only)")
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    audit_repo = AuditRepository(db)
    return await audit_repo.get_logs(skip=skip, limit=limit)
