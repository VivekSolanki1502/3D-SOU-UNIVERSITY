import uuid
from typing import Any, Dict, Optional
from sqlalchemy import JSON, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # CREATE, UPDATE, DELETE, PUBLISH, UNPUBLISH, ROLE_CHANGE
    entity_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)  # building, room, facility, event, exam, sos, user
    entity_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_audit_logs_actor_action", "actor_id", "action"),
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
    )
