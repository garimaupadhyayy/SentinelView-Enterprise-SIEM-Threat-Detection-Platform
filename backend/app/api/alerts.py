from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_analyst_or_admin, require_any_role
from app.models.alert import Alert, AlertStatus
from app.models.event import Event, Severity
from app.models.user import User
from app.schemas.alert import AlertOut, AlertStatusUpdate
from app.schemas.event import EventOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    severity: Severity | None = None,
    status_filter: AlertStatus | None = Query(None, alias="status"),
    source_ip: str | None = None,
    mitre_technique_id: str | None = None,
    sort_by: str = Query("created_at", pattern="^(created_at|severity|last_seen)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(50, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    query = db.query(Alert)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status_filter:
        query = query.filter(Alert.status == status_filter)
    if source_ip:
        query = query.filter(Alert.source_ip == source_ip)
    if mitre_technique_id:
        query = query.filter(Alert.mitre_technique_id == mitre_technique_id)

    sort_col = getattr(Alert, sort_by)
    query = query.order_by(sort_col.desc() if order == "desc" else sort_col.asc())

    return query.offset(offset).limit(limit).all()


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db), _: User = Depends(require_any_role)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
    return alert


@router.get("/{alert_id}/events", response_model=list[EventOut])
def get_alert_events(alert_id: int, db: Session = Depends(get_db), _: User = Depends(require_any_role)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
    ids = [int(i) for i in (alert.related_event_ids or "").split(",") if i]
    if not ids:
        return []
    return db.query(Event).filter(Event.id.in_(ids)).order_by(Event.timestamp.desc()).all()


@router.patch("/{alert_id}/status", response_model=AlertOut)
def update_alert_status(
    alert_id: int,
    payload: AlertStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_analyst_or_admin),
):
    """Analysts (and admins) triage alerts through the SOC workflow:
    New -> Investigating -> Resolved / False Positive. Viewers are read-only."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
    alert.status = payload.status
    db.commit()
    db.refresh(alert)
    return alert
