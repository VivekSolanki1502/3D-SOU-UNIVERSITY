import uuid
from typing import List, Optional
from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Building(Base, TimestampMixin):
    __tablename__ = "buildings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    short_code: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    department: Mapped[str | None] = mapped_column(String(150), nullable=True)
    faculty_lead: Mapped[str | None] = mapped_column(String(150), nullable=True)
    floors_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # 3D Coordinates & Dimensions for Three.js engine
    pos_x: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pos_z: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    dim_w: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    dim_d: Mapped[float] = mapped_column(Float, default=3.0, nullable=False)
    dim_h: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    floors: Mapped[List["Floor"]] = relationship("Floor", back_populates="building", cascade="all, delete-orphan")
    rooms: Mapped[List["Room"]] = relationship("Room", back_populates="building", cascade="all, delete-orphan")


class Floor(Base, TimestampMixin):
    __tablename__ = "floors"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    building_id: Mapped[str] = mapped_column(String(64), ForeignKey("buildings.id", ondelete="CASCADE"), index=True, nullable=False)
    floor_number: Mapped[int] = mapped_column(Integer, nullable=False)
    floor_label: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    building: Mapped["Building"] = relationship("Building", back_populates="floors")


class Room(Base, TimestampMixin):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    building_id: Mapped[str] = mapped_column(String(64), ForeignKey("buildings.id", ondelete="CASCADE"), index=True, nullable=False)
    floor_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    room_number: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # lab, workshop, library, hall, staff-room, cell, classroom, faculty-office
    department: Mapped[str | None] = mapped_column(String(150), nullable=True)
    faculty_in_charge: Mapped[str | None] = mapped_column(String(150), nullable=True)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # 3D Integration metadata
    model_id: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    coordinates_3d: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    aliases: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_accessible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    building: Mapped["Building"] = relationship("Building", back_populates="rooms")

    __table_args__ = (
        Index("ix_rooms_type_active", "room_type", "is_active"),
        Index("ix_rooms_building_floor", "building_id", "floor_number"),
    )


class Facility(Base, TimestampMixin):
    __tablename__ = "facilities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    facility_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # canteen, parking, medical, auditorium, gate, sports
    building_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    location_description: Mapped[str] = mapped_column(String(255), nullable=False)
    code_symbol: Mapped[str | None] = mapped_column(String(10), nullable=True)
    aliases: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_accessible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
