from typing import List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.campus import Building, Floor, Room, Facility
from app.db.repositories.base import BaseRepository


class CampusRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.buildings = BaseRepository[Building](Building, db)
        self.floors = BaseRepository[Floor](Floor, db)
        self.rooms = BaseRepository[Room](Room, db)
        self.facilities = BaseRepository[Facility](Facility, db)

    # Building queries
    async def get_active_buildings(self) -> List[Building]:
        result = await self.db.execute(select(Building).where(Building.is_active == True))
        return list(result.scalars().all())

    async def get_active_building(self, building_id: str) -> Optional[Building]:
        result = await self.db.execute(
            select(Building).where(Building.id == building_id, Building.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_floors_by_building(self, building_id: str) -> List[Floor]:
        result = await self.db.execute(
            select(Floor).where(Floor.building_id == building_id).order_by(Floor.floor_number.asc())
        )
        return list(result.scalars().all())

    # Room queries
    async def get_active_rooms(
        self,
        building_id: Optional[str] = None,
        room_type: Optional[str] = None,
        limit: int = 500,
    ) -> List[Room]:
        query = select(Room).join(Building).where(
            Room.is_active.is_(True),
            Building.is_active.is_(True),
        )
        if building_id:
            query = query.where(Room.building_id == building_id)
        if room_type:
            query = query.where(Room.room_type == room_type.lower())
        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # Facility queries
    async def get_active_facilities(self, facility_type: Optional[str] = None) -> List[Facility]:
        query = select(Facility).where(Facility.is_active == True)
        if facility_type:
            query = query.where(Facility.facility_type == facility_type.lower())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # Unified Search
    async def search_campus(self, query_str: str) -> List[dict]:
        q = f"%{query_str.strip().lower()}%"
        results = []

        # 1. Search Buildings
        b_res = await self.db.execute(
            select(Building).where(
                Building.is_active == True,
                or_(
                    Building.name.ilike(q),
                    Building.short_code.ilike(q),
                    Building.department.ilike(q),
                    Building.faculty_lead.ilike(q)
                )
            )
        )
        for b in b_res.scalars().all():
            results.append({
                "id": b.id,
                "name": b.name,
                "category": "building",
                "subtitle": f"{b.short_code} · {b.floors_count} Floors · {b.department or 'Campus Block'}",
                "code": b.short_code,
                "building_id": b.id,
                "floor_number": 0,
                "model_id": b.id,
                "coordinates_3d": {"x": b.pos_x, "z": b.pos_z, "w": b.dim_w, "d": b.dim_d, "h": b.dim_h},
                "is_accessible": True
            })

        # 2. Search Rooms
        r_res = await self.db.execute(
            select(Room).join(Building).where(
                Room.is_active == True,
                Building.is_active.is_(True),
                or_(
                    Room.name.ilike(q),
                    Room.room_number.ilike(q),
                    Room.department.ilike(q),
                    Room.faculty_in_charge.ilike(q),
                    Room.room_type.ilike(q)
                )
            )
        )
        for r in r_res.scalars().all():
            results.append({
                "id": r.id,
                "name": r.name,
                "category": r.room_type,
                "subtitle": f"{r.building_id.upper()} · Floor {r.floor_number} · {r.room_number}",
                "code": r.room_number,
                "building_id": r.building_id,
                "floor_number": r.floor_number,
                "model_id": r.model_id or r.id,
                "coordinates_3d": r.coordinates_3d,
                "is_accessible": r.is_accessible
            })

        # 3. Search Facilities
        f_res = await self.db.execute(
            select(Facility).where(
                Facility.is_active == True,
                or_(
                    Facility.name.ilike(q),
                    Facility.facility_type.ilike(q),
                    Facility.location_description.ilike(q)
                )
            )
        )
        for f in f_res.scalars().all():
            results.append({
                "id": f.id,
                "name": f.name,
                "category": "facility",
                "subtitle": f.location_description,
                "code": f.code_symbol,
                "building_id": f.building_id,
                "floor_number": 0,
                "model_id": f.id,
                "coordinates_3d": {},
                "is_accessible": f.is_accessible
            })

        return results
