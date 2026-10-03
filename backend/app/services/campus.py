from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import cache_delete_pattern, cache_get, cache_set
from app.db.models.campus import Building, Floor, Room, Facility
from app.db.repositories.campus import CampusRepository
from app.schemas.campus import (
    BuildingCreate, BuildingUpdate,
    FloorCreate,
    RoomCreate, RoomUpdate,
    FacilityCreate, FacilityUpdate
)


class CampusService:
    def __init__(self, db: AsyncSession):
        self.repo = CampusRepository(db)

    async def get_all_buildings(self) -> List[Building]:
        cache_key = "campus:buildings:all"
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached
        
        buildings = await self.repo.get_active_buildings()
        result = [
            {
                "id": b.id,
                "name": b.name,
                "short_code": b.short_code,
                "department": b.department,
                "faculty_lead": b.faculty_lead,
                "floors_count": b.floors_count,
                "pos_x": b.pos_x,
                "pos_z": b.pos_z,
                "dim_w": b.dim_w,
                "dim_d": b.dim_d,
                "dim_h": b.dim_h,
                "description": b.description,
                "aliases": b.aliases,
                "metadata_json": b.metadata_json,
                "is_active": b.is_active,
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "updated_at": b.updated_at.isoformat() if b.updated_at else None,
            }
            for b in buildings
        ]
        await cache_set(cache_key, result, ttl_seconds=600)
        return buildings

    async def get_building(self, building_id: str) -> Optional[Building]:
        return await self.repo.get_active_building(building_id)

    async def get_floors_by_building(self, building_id: str) -> List[Floor]:
        return await self.repo.get_floors_by_building(building_id)

    async def create_building(self, building_in: BuildingCreate) -> Building:
        b = Building(**building_in.model_dump())
        created = await self.repo.buildings.create(b)
        await cache_delete_pattern("campus:*")
        return created

    async def update_building(self, building_id: str, building_in: BuildingUpdate) -> Optional[Building]:
        updated = await self.repo.buildings.update(building_id, building_in.model_dump(exclude_unset=True))
        await cache_delete_pattern("campus:*")
        return updated

    async def delete_building(self, building_id: str) -> bool:
        deleted = await self.repo.buildings.delete(building_id)
        if deleted:
            await cache_delete_pattern("campus:*")
        return deleted

    # Room operations
    async def get_rooms(self, building_id: Optional[str] = None, room_type: Optional[str] = None) -> List[Room]:
        cache_key = f"campus:rooms:{building_id}:{room_type}"
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached

        rooms = await self.repo.get_active_rooms(
            building_id=building_id,
            room_type=room_type,
            limit=500,
        )

        # Cache lightweight list
        await cache_set(cache_key, [
            {
                "id": r.id,
                "building_id": r.building_id,
                "floor_number": r.floor_number,
                "room_number": r.room_number,
                "name": r.name,
                "room_type": r.room_type,
                "department": r.department,
                "faculty_in_charge": r.faculty_in_charge,
                "capacity": r.capacity,
                "model_id": r.model_id,
                "coordinates_3d": r.coordinates_3d,
                "aliases": r.aliases,
                "is_accessible": r.is_accessible,
                "is_active": r.is_active,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in rooms
        ], ttl_seconds=300)
        return rooms

    async def create_room(self, room_in: RoomCreate) -> Room:
        r = Room(**room_in.model_dump())
        created = await self.repo.rooms.create(r)
        await cache_delete_pattern("campus:*")
        return created

    async def update_room(self, room_id: str, room_in: RoomUpdate) -> Optional[Room]:
        updated = await self.repo.rooms.update(room_id, room_in.model_dump(exclude_unset=True))
        await cache_delete_pattern("campus:*")
        return updated

    async def delete_room(self, room_id: str) -> bool:
        deleted = await self.repo.rooms.delete(room_id)
        if deleted:
            await cache_delete_pattern("campus:*")
        return deleted

    # Facility operations
    async def get_facilities(self, facility_type: Optional[str] = None) -> List[Facility]:
        return await self.repo.get_active_facilities(facility_type)

    async def create_facility(self, facility_in: FacilityCreate) -> Facility:
        f = Facility(**facility_in.model_dump())
        created = await self.repo.facilities.create(f)
        await cache_delete_pattern("campus:*")
        return created

    async def update_facility(self, facility_id: str, facility_in: FacilityUpdate) -> Optional[Facility]:
        updated = await self.repo.facilities.update(facility_id, facility_in.model_dump(exclude_unset=True))
        await cache_delete_pattern("campus:*")
        return updated

    async def delete_facility(self, facility_id: str) -> bool:
        deleted = await self.repo.facilities.delete(facility_id)
        if deleted:
            await cache_delete_pattern("campus:*")
        return deleted

    # Search
    async def search(self, query: str) -> List[dict]:
        cache_key = f"campus:search:{query.strip().lower()}"
        cached = await cache_get(cache_key)
        if cached is not None:
            return cached
        
        results = await self.repo.search_campus(query)
        await cache_set(cache_key, results, ttl_seconds=120)
        return results
