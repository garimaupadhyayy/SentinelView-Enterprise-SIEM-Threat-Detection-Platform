from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_any_role
from app.models.alert import Alert, AlertStatus
from app.models.event import Event, Severity
from app.models.user import User
from app.services import geoip_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(
    minutes: int = Query(60, description="Lookback window in minutes for events/sec"),
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=minutes)

    total_events_window = db.query(Event).filter(Event.timestamp >= window_start).count()
    events_per_sec = round(total_events_window / (minutes * 60), 3) if minutes else 0

    total_events = db.query(Event).count()
    total_alerts = db.query(Alert).count()

    alert_counts_by_severity = dict(
        db.query(Alert.severity, func.count(Alert.id)).group_by(Alert.severity).all()
    )
    alert_counts_by_status = dict(
        db.query(Alert.status, func.count(Alert.id)).group_by(Alert.status).all()
    )

    top_source_ips = (
        db.query(Event.source_ip, func.count(Event.id).label("cnt"))
        .filter(Event.source_ip.isnot(None), Event.timestamp >= window_start)
        .group_by(Event.source_ip)
        .order_by(func.count(Event.id).desc())
        .limit(10)
        .all()
    )

    new_alerts = db.query(Alert).filter(Alert.status == AlertStatus.NEW).count()

    return {
        "generated_at": now.isoformat(),
        "window_minutes": minutes,
        "total_events": total_events,
        "total_events_in_window": total_events_window,
        "events_per_second": events_per_sec,
        "total_alerts": total_alerts,
        "new_alerts": new_alerts,
        "alert_counts_by_severity": {
            (s.value if isinstance(s, Severity) else s): c for s, c in alert_counts_by_severity.items()
        },
        "alert_counts_by_status": {
            (s.value if isinstance(s, AlertStatus) else s): c for s, c in alert_counts_by_status.items()
        },
        "top_source_ips": [{"source_ip": ip, "count": cnt} for ip, cnt in top_source_ips],
    }


@router.get("/geomap")
def geomap(
    minutes: int = Query(60, description="Lookback window in minutes"),
    limit: int = Query(200, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    """
    Returns geolocated points for source IPs seen recently, for the
    dashboard's geo-map widget. Uses the free ip-api.com lookup with a
    Redis cache -- see app/services/geoip_service.py.
    """
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=minutes)

    ips = (
        db.query(Event.source_ip, func.count(Event.id).label("cnt"))
        .filter(Event.source_ip.isnot(None), Event.timestamp >= window_start)
        .group_by(Event.source_ip)
        .order_by(func.count(Event.id).desc())
        .limit(limit)
        .all()
    )

    points = []
    for ip, cnt in ips:
        loc = geoip_service.lookup_ip(ip)
        if loc:
            points.append(
                {
                    "source_ip": ip,
                    "count": cnt,
                    "lat": loc["lat"],
                    "lon": loc["lon"],
                    "city": loc["city"],
                    "country": loc["country"],
                }
            )
    return {"points": points}


@router.get("/mitre-heatmap")
def mitre_heatmap(
    days: int = Query(7, description="Lookback window in days"),
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    """Counts alerts per MITRE ATT&CK technique for the heatmap widget."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=days)

    rows = (
        db.query(Alert.mitre_technique_id, Alert.mitre_technique_name, func.count(Alert.id))
        .filter(Alert.created_at >= window_start, Alert.mitre_technique_id.isnot(None))
        .group_by(Alert.mitre_technique_id, Alert.mitre_technique_name)
        .all()
    )

    return {
        "techniques": [
            {"technique_id": tid, "technique_name": name, "count": count}
            for tid, name, count in rows
        ]
    }


@router.get("/events-timeseries")
def events_timeseries(
    hours: int = Query(24, le=168),
    bucket_minutes: int = Query(30, ge=1, le=180),
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    """Bucketed event counts for the dashboard's activity-over-time chart."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=hours)

    events = (
        db.query(Event.timestamp)
        .filter(Event.timestamp >= window_start)
        .order_by(Event.timestamp)
        .all()
    )

    bucket_seconds = bucket_minutes * 60
    counter: Counter = Counter()
    for (ts,) in events:
        ts_aware = ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
        bucket_epoch = int(ts_aware.timestamp() // bucket_seconds) * bucket_seconds
        counter[bucket_epoch] += 1

    buckets = [
        {"timestamp": datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(), "count": count}
        for epoch, count in sorted(counter.items())
    ]
    return {"bucket_minutes": bucket_minutes, "buckets": buckets}
