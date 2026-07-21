from datetime import datetime

from sqlalchemy import Boolean, DateTime, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class DetectionRule(Base):
    """
    A configurable correlation rule. Built-in rules are seeded on startup
    (see app/rules/builtin_rules.py) but are stored here just like any
    user-created rule, so the "custom rule builder" in the UI is editing
    the exact same objects the engine evaluates — no special-casing.
    """

    __tablename__ = "detection_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    rule_type: Mapped[str] = mapped_column(String(64), nullable=False)
    # one of: brute_force, port_scan, impossible_travel, priv_escalation,
    # web_attack_signature, threshold_generic (custom)

    mitre_technique_id: Mapped[str | None] = mapped_column(String(16), nullable=True)
    mitre_technique_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    severity: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    weight: Mapped[int] = mapped_column(default=1)  # contributes to computed alert severity score

    # Free-form JSON config so new rules = new config entry, not new code.
    # e.g. {"window_seconds": 300, "threshold": 5, "event_type": "auth_failure"}
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
