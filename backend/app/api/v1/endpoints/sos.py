from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import get_optional_current_user, require_admin
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.sos import SOSContactCreate, SOSContactResponse, SOSContactUpdate
from app.services.sos import SOSService

router = APIRouter()


@router.get("", response_model=List[SOSContactResponse], summary="List active SOS emergency contacts (All users)")
async def list_sos_contacts(
    category: Optional[str] = Query(None, description="Category filter (security, medical, fire, etc.)"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = SOSService(db)
    is_admin = current_user is not None and current_user.role.lower() == "admin"
    return await service.get_active_contacts(category=category, include_inactive=is_admin)


@router.get("/{contact_id}", response_model=SOSContactResponse, summary="Get single SOS contact")
async def get_sos_contact(
    contact_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SOSService(db)
    contact = await service.get_contact(contact_id)
    is_admin = current_user is not None and current_user.role.lower() == "admin"
    if not contact or (not contact.is_active and not is_admin):
        raise HTTPException(status_code=404, detail="SOS contact not found")
    return contact


@router.post("", response_model=SOSContactResponse, status_code=status.HTTP_201_CREATED, summary="Create SOS contact (Admin only)")
async def create_sos_contact(
    contact_in: SOSContactCreate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = SOSService(db)
    return await service.create_contact(contact_in)


@router.patch("/{contact_id}", response_model=SOSContactResponse, summary="Update SOS contact (Admin only)")
async def update_sos_contact(
    contact_id: str,
    contact_in: SOSContactUpdate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = SOSService(db)
    updated = await service.update_contact(contact_id, contact_in)
    if not updated:
        raise HTTPException(status_code=404, detail="SOS contact not found")
    return updated


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete SOS contact (Admin only)")
async def delete_sos_contact(
    contact_id: str,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = SOSService(db)
    deleted = await service.delete_contact(contact_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="SOS contact not found")
