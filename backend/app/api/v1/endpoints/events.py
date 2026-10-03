from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import get_optional_current_user, require_admin
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services.event import EventService

router = APIRouter()


@router.get("", response_model=List[EventResponse], summary="List published campus events")
async def list_events(
    category: Optional[str] = Query(None, description="Filter by event category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = EventService(db)
    is_admin = current_user is not None and current_user.role.lower() == "admin"
    return await service.get_published_events(
        category=category,
        skip=skip,
        limit=limit,
        include_unpublished=is_admin,
    )


@router.get("/{event_id}", response_model=EventResponse, summary="Get single event details")
async def get_event(
    event_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = EventService(db)
    event = await service.get_event(event_id)
    is_admin = current_user is not None and current_user.role.lower() == "admin"
    if not event or (not event.is_published and not is_admin):
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED, summary="Create event (Admin only)")
async def create_event(
    event_in: EventCreate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = EventService(db)
    return await service.create_event(event_in, user_id=current_admin.id)


@router.patch("/{event_id}", response_model=EventResponse, summary="Update event (Admin only)")
async def update_event(
    event_id: str,
    event_in: EventUpdate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = EventService(db)
    updated = await service.update_event(event_id, event_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete event (Admin only)")
async def delete_event(
    event_id: str,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = EventService(db)
    deleted = await service.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
