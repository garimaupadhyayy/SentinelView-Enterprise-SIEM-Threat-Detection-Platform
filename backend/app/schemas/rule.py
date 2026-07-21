from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: str
    mitre_technique_id: Optional[str] = None
    mitre_technique_name: Optional[str] = None
    severity: str = "medium"
    weight: int = 1
    config: dict = {}
    enabled: bool = True


class RuleUpdate(BaseModel):
    description: Optional[str] = None
    severity: Optional[str] = None
    weight: Optional[int] = None
    config: Optional[dict] = None
    enabled: Optional[bool] = None


class RuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str]
    rule_type: str
    mitre_technique_id: Optional[str]
    mitre_technique_name: Optional[str]
    severity: str
    weight: int
    config: dict
    enabled: bool
    is_builtin: bool
    created_at: datetime
    updated_at: datetime
