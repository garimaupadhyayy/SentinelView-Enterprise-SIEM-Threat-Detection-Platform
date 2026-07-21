from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.alert import AlertStatus
from app.models.event import Severity


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    rule_id: Optional[int]
    rule_name: str
    mitre_technique_id: Optional[str]
    mitre_technique_name: Optional[str]
    severity: Severity
    status: AlertStatus
    source_ip: Optional[str]
    target: Optional[str]
    title: str
    description: str
    event_count: int
    first_seen: datetime
    last_seen: datetime
    created_at: datetime
    updated_at: datetime


class AlertStatusUpdate(BaseModel):
    status: AlertStatus


class AlertFilterParams(BaseModel):
    severity: Optional[Severity] = None
    status: Optional[AlertStatus] = None
    source_ip: Optional[str] = None
    mitre_technique_id: Optional[str] = None
    limit: int = 50
    offset: int = 0
