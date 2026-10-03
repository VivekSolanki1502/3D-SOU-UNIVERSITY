import uuid
from datetime import date, time
from sqlalchemy import Boolean, Date, ForeignKey, Index, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="academic", index=True, nullable=False)  # academic, cultural, sports, workshop, tech-fest
    event_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    venue: Mapped[str] = mapped_column(String(150), nullable=False)
    building_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    room_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    organizer: Mapped[str | None] = mapped_column(String(150), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        Index("ix_events_published_date", "is_published", "event_date"),
    )
