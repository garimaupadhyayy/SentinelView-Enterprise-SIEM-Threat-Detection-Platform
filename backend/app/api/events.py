from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.deps import require_analyst_or_admin, require_any_role
from app.models.event import Event, Severity, SourceType
from app.models.user import User
from app.parsers import get_parser
from app.schemas.event import EventOut, EventPushRequest
from app.services.ingestion_service import IngestionService
from app.ws.manager import manager

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/upload", response_model=list[EventOut], status_code=status.HTTP_201_CREATED)
async def upload_log_file(
    source_type: str = Query(..., description="One of: ssh_auth, web_access, firewall"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_analyst_or_admin),
):
    """
    Accepts a raw log file (syslog/auth.log, Apache/Nginx access log, or
    iptables/firewall log), runs it through the matching parser, normalizes
    every recognized line, and stores + correlates the result.
    """
    try:
        parser = get_parser(source_type)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))

    raw_bytes = await file.read()
    try:
        text = raw_bytes.decode("utf-8", errors="ignore")
    except Exception:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Could not decode file as text")

    lines = text.splitlines()
    normalized = parser.parse_lines(lines)
    if not normalized:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"No lines matched the '{source_type}' parser format. "
            f"{len(lines)} lines were read from the file.",
        )

    service = IngestionService(db)
    db_events = service.ingest_events(normalized, source_name=file.filename or "file-upload")

    for e in db_events:
        await manager.broadcast_event(
            {"type": "event", "data": EventOut.model_validate(e).model_dump()}
        )
    for a in service.last_alerts:
        from app.schemas.alert import AlertOut

        await manager.broadcast_alert(
            {"type": "alert", "data": AlertOut.model_validate(a).model_dump()}
        )

    return db_events


@router.post("/push", response_model=list[EventOut], status_code=status.HTTP_201_CREATED)
async def push_events(
    payload: EventPushRequest,
    db: Session = Depends(get_db),
    x_api_key: str = Query(default="", alias="api_key"),
):
    """
    Programmatic REST ingestion endpoint used by the log-shipper agent and
    any other external forwarder. Authenticated via a shared API key rather
    than a user JWT since this is machine-to-machine traffic.
    """
    if x_api_key != settings.INGEST_API_KEY:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing api_key")

    if payload.events:
        normalized = payload.events
    elif payload.raw_lines:
        try:
            parser = get_parser(payload.source_type.value)
        except ValueError as exc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
        normalized = parser.parse_lines(payload.raw_lines)
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Provide either 'events' or 'raw_lines'")

    if not normalized:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "No events could be parsed")

    service = IngestionService(db)
    db_events = service.ingest_events(normalized, source_name=payload.source_name or "api-push")

    for e in db_events:
        await manager.broadcast_event(
            {"type": "event", "data": EventOut.model_validate(e).model_dump()}
        )
    for a in service.last_alerts:
        from app.schemas.alert import AlertOut

        await manager.broadcast_alert(
            {"type": "alert", "data": AlertOut.model_validate(a).model_dump()}
        )

    return db_events


@router.get("/search", response_model=list[EventOut])
def search_events(
    q: Optional[str] = Query(None, description="Full-text search across raw_message"),
    source_ip: Optional[str] = None,
    severity: Optional[Severity] = None,
    source_type: Optional[SourceType] = None,
    event_type: Optional[str] = None,
    user_field: Optional[str] = Query(None, alias="user"),
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    query = db.query(Event)

    if q:
        query = query.filter(
            or_(Event.raw_message.contains(q), Event.url_path.contains(q))
        )
    if source_ip:
        query = query.filter(Event.source_ip == source_ip)
    if severity:
        query = query.filter(Event.severity == severity)
    if source_type:
        query = query.filter(Event.source_type == source_type)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if user_field:
        query = query.filter(Event.user == user_field)
    if start:
        query = query.filter(Event.timestamp >= start)
    if end:
        query = query.filter(Event.timestamp <= end)

    return (
        query.order_by(Event.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
