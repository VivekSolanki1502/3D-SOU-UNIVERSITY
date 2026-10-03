import uuid
from sqlalchemy import Boolean, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class SOSContact(Base, TimestampMixin):
    __tablename__ = "sos_contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False)  # security, medical, fire, helpline, ambulance, women_safety
    phone_number: Mapped[str] = mapped_column(String(50), nullable=False)
    alternate_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location_name: Mapped[str] = mapped_column(String(150), nullable=False)
    building_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    room_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    coordinates_3d: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    available_hours: Mapped[str] = mapped_column(String(100), default="24/7", nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)

    __table_args__ = (
        Index("ix_sos_category_active", "category", "is_active"),
    )
