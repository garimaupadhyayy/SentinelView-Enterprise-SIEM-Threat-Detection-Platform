from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.event import Severity, SourceType


class NormalizedEventIn(BaseModel):
    """The unified schema every parser and the REST push endpoint produce."""

    timestamp: datetime
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    event_type: str
    severity: Severity = Severity.INFO
    raw_message: str
    source_type: SourceType
    user: Optional[str] = None
    status_code: Optional[str] = None
    port: Optional[int] = None
    url_path: Optional[str] = None


class EventOut(NormalizedEventIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ingested_at: datetime


class EventPushRequest(BaseModel):
    """Body for the programmatic REST ingestion endpoint."""

    source_type: SourceType
    # Accept either raw lines (parsed server-side) or already-normalized events
    raw_lines: Optional[list[str]] = None
    events: Optional[list[NormalizedEventIn]] = None
    source_name: Optional[str] = "api-push"
