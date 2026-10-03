import uuid
from datetime import date, time
from sqlalchemy import Date, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class Exam(Base, TimestampMixin):
    __tablename__ = "exams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    subject_code: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    course: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # B.Tech, Diploma, MCA, etc.
    department: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # CSE, IT, Mechanical, etc.
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    exam_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    venue: Mapped[str] = mapped_column(String(150), nullable=False)
    building_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    room_id: Mapped[str | None] = mapped_column(String(64), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="scheduled", index=True, nullable=False)  # scheduled, ongoing, completed, rescheduled, cancelled
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    __table_args__ = (
        Index("ix_exams_dept_sem_date", "department", "semester", "exam_date"),
    )
