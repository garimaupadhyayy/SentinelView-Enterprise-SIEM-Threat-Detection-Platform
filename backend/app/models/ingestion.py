from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class IngestionSource(Base):
    """Tracks a named source that is pushing logs in (e.g. a log-shipper agent instance)."""

    __tablename__ = "ingestion_sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    host: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
