import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.event import Severity


class AlertStatus(str, enum.Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    rule_id: Mapped[int | None] = mapped_column(ForeignKey("detection_rules.id"), nullable=True)
    rule_name: Mapped[str] = mapped_column(String(128), nullable=False)
    mitre_technique_id: Mapped[str | None] = mapped_column(String(16), nullable=True)  # e.g. T1110
    mitre_technique_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.MEDIUM, nullable=False)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.NEW, nullable=False)

    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    target: Mapped[str | None] = mapped_column(String(128), nullable=True)  # user/host targeted

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # event ids that triggered this alert, comma-separated for simplicity in MVP
    related_event_ids: Mapped[str] = mapped_column(Text, nullable=True)
    event_count: Mapped[int] = mapped_column(Integer, default=1)

    # dedup key used in redis to correlate repeat firings of the same rule/source
    dedup_key: Mapped[str] = mapped_column(String(255), nullable=False)

    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_alerts_severity", "severity"),
        Index("ix_alerts_status", "status"),
        Index("ix_alerts_created_at", "created_at"),
        Index("ix_alerts_source_ip", "source_ip"),
    )
