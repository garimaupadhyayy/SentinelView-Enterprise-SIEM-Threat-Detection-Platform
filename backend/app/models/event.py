import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Severity(str, enum.Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SourceType(str, enum.Enum):
    SSH_AUTH = "ssh_auth"
    WEB_ACCESS = "web_access"
    FIREWALL = "firewall"
    WINDOWS_EVENT = "windows_event"
    GENERIC = "generic"


class Event(Base):
    """
    Unified normalized log event. Every parser (ssh, web access, firewall, ...)
    maps its source-specific format into this single schema so the
    correlation engine and search/UI layers never need to know the source
    format.
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv4/IPv6
    destination_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)  # e.g. auth_failure, http_request
    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.INFO, nullable=False)
    raw_message: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False)
    user: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status_code: Mapped[str | None] = mapped_column(String(16), nullable=True)

    # extra structured fields useful for detection rules without over-normalizing
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    url_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_events_timestamp", "timestamp"),
        Index("ix_events_source_ip", "source_ip"),
        Index("ix_events_severity", "severity"),
        Index("ix_events_source_ip_timestamp", "source_ip", "timestamp"),
    )
