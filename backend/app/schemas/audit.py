from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: str
    actor_id: Optional[str] = None
    actor_email: Optional[str] = None
    action: str
    entity_type: str
    entity_id: str
    details: Optional[str] = None
    metadata_json: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
