from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_admin
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.campus import (
    BuildingCreate, BuildingResponse, BuildingUpdate,
    CampusSearchResult,
    FacilityCreate, FacilityResponse, FacilityUpdate,
    FloorResponse,
    RoomCreate, RoomResponse, RoomUpdate
)
from app.services.campus import CampusService

router = APIRouter()


# ==========================================
# 3D Campus Unified Search
# ==========================================
@router.get("/search", response_model=List[CampusSearchResult], summary="Search 3D Campus entities")
async def search_campus(
    q: str = Query(..., min_length=1, max_length=100, description="Search term for building, room, lab, etc."),
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    return await service.search(q)


# ==========================================
# Buildings
# ==========================================
@router.get("/buildings", response_model=List[BuildingResponse], summary="List all active campus buildings")
async def list_buildings(db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    return await service.get_all_buildings()


@router.get("/buildings/{building_id}/floors", response_model=List[FloorResponse], summary="List floors in a campus building")
async def list_building_floors(building_id: str, db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    if not await service.get_building(building_id):
        raise HTTPException(status_code=404, detail="Building not found")
    return await service.get_floors_by_building(building_id)


@router.get("/buildings/{building_id}", response_model=BuildingResponse, summary="Get single building details")
async def get_building(building_id: str, db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    building = await service.get_building(building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building


@router.post("/buildings", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED, summary="Create building (Admin only)")
async def create_building(
    building_in: BuildingCreate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    return await service.create_building(building_in)


@router.patch("/buildings/{building_id}", response_model=BuildingResponse, summary="Update building (Admin only)")
async def update_building(
    building_id: str,
    building_in: BuildingUpdate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    updated = await service.update_building(building_id, building_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Building not found")
    return updated


@router.delete("/buildings/{building_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete building (Admin only)")
async def delete_building(
    building_id: str,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    deleted = await service.delete_building(building_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Building not found")


# ==========================================
# Rooms & Categorized Facilities
# ==========================================
@router.get("/rooms", response_model=List[RoomResponse], summary="List rooms filtered by building or type")
async def list_rooms(
    building_id: Optional[str] = None,
    room_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    return await service.get_rooms(building_id=building_id, room_type=room_type)


@router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED, summary="Create room (Admin only)")
async def create_room(
    room_in: RoomCreate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    return await service.create_room(room_in)


@router.patch("/rooms/{room_id}", response_model=RoomResponse, summary="Update room (Admin only)")
async def update_room(
    room_id: str,
    room_in: RoomUpdate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    updated = await service.update_room(room_id, room_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Room not found")
    return updated


@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete room (Admin only)")
async def delete_room(
    room_id: str,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    deleted = await service.delete_room(room_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")


# Categorized convenience room routes
@router.get("/labs", response_model=List[RoomResponse], summary="List all computer and engineering labs")
async def get_labs(db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    return await service.get_rooms(room_type="lab")


@router.get("/workshops", response_model=List[RoomResponse], summary="List all workshops")
async def get_workshops(db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    return await service.get_rooms(room_type="workshop")


@router.get("/libraries", response_model=List[RoomResponse], summary="List all libraries")
async def get_libraries(db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    return await service.get_rooms(room_type="library")


@router.get("/halls", response_model=List[RoomResponse], summary="List seminar halls and auditoriums")
async def get_halls(db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    return await service.get_rooms(room_type="hall")


@router.get("/staff-rooms", response_model=List[RoomResponse], summary="List staff rooms")
async def get_staff_rooms(db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    return await service.get_rooms(room_type="staff-room")


@router.get("/cells", response_model=List[RoomResponse], summary="List cells & committees (Placement, Anti-Ragging, etc.)")
async def get_cells(db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    return await service.get_rooms(room_type="cell")


@router.get("/faculties", response_model=List[RoomResponse], summary="List faculty cabins and offices")
async def get_faculty_cabins(db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    return await service.get_rooms(room_type="faculty-office")


# ==========================================
# Facilities (Canteens, Gates, Parking, etc.)
# ==========================================
@router.get("/facilities", response_model=List[FacilityResponse], summary="List general campus facilities")
async def list_facilities(facility_type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    service = CampusService(db)
    return await service.get_facilities(facility_type)


@router.post("/facilities", response_model=FacilityResponse, status_code=status.HTTP_201_CREATED, summary="Create facility (Admin only)")
async def create_facility(
    facility_in: FacilityCreate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    return await service.create_facility(facility_in)


@router.patch("/facilities/{facility_id}", response_model=FacilityResponse, summary="Update facility (Admin only)")
async def update_facility(
    facility_id: str,
    facility_in: FacilityUpdate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    updated = await service.update_facility(facility_id, facility_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Facility not found")
    return updated


@router.delete("/facilities/{facility_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete facility (Admin only)")
async def delete_facility(
    facility_id: str,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = CampusService(db)
    deleted = await service.delete_facility(facility_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Facility not found")
