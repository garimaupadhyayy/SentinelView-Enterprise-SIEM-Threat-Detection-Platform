import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis_client import redis_safe_expire, redis_safe_get, redis_safe_setex
from app.models.alert import Alert, AlertStatus
from app.models.event import Severity
from app.models.rule import DetectionRule
from app.services.notification_service import dispatch_critical_notification

_SEVERITY_ORDER = [Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]


def score_severity(base_severity: str, rule_weight: int, occurrence_count: int) -> Severity:
    """
    Combines the rule's configured base severity with its weight and how many
    times it has fired in the current window to bump severity up -- e.g. a
    medium-severity rule that keeps re-triggering escalates to high/critical,
    which mirrors how a real SOC would triage repeat offenders more urgently.
    """
    try:
        idx = _SEVERITY_ORDER.index(Severity(base_severity))
    except ValueError:
        idx = 2  # default medium

    bump = 0
    if occurrence_count >= 20 or rule_weight >= 3 and occurrence_count >= 10:
        bump = 2
    elif occurrence_count >= 8 or (rule_weight >= 3 and occurrence_count >= 3):
        bump = 1

    idx = min(idx + bump, len(_SEVERITY_ORDER) - 1)
    return _SEVERITY_ORDER[idx]


def _dedup_key(rule_name: str, source_ip: str | None, target: str | None) -> str:
    raw = f"{rule_name}:{source_ip or '-'}:{target or '-'}"
    return "alert_dedup:" + hashlib.sha256(raw.encode()).hexdigest()[:32]


class AlertService:
    """
    Creates/updates alerts while deduplicating repeat firings of the same
    rule against the same source/target within ALERT_DEDUP_WINDOW_SECONDS,
    using Redis as a fast, TTL-based dedup cache -- this is the "avoid
    alert fatigue" requirement from the spec.
    """

    def __init__(self, db: Session):
        self.db = db

    def raise_alert(
        self,
        rule: DetectionRule,
        title: str,
        description: str,
        source_ip: str | None,
        target: str | None,
        related_event_ids: list[int],
        occurrence_count: int = 1,
    ) -> Alert:
        dedup_key = _dedup_key(rule.name, source_ip, target)
        cache_hit = redis_safe_get(dedup_key)

        severity = score_severity(rule.severity, rule.weight, occurrence_count)
        now = datetime.now(timezone.utc)

        if cache_hit:
            # Same rule + same source/target fired again inside the dedup
            # window: update the existing alert instead of creating a new
            # row (this is exactly the alert-fatigue problem the spec calls out).
            alert_id = int(cache_hit)
            alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
            if alert:
                alert.last_seen = now
                alert.event_count = (alert.event_count or 1) + 1
                alert.severity = score_severity(rule.severity, rule.weight, alert.event_count)
                existing_ids = set(
                    filter(None, (alert.related_event_ids or "").split(","))
                )
                existing_ids.update(str(i) for i in related_event_ids)
                alert.related_event_ids = ",".join(sorted(existing_ids, key=int))
                self.db.commit()
                self.db.refresh(alert)
                redis_safe_expire(dedup_key, settings.ALERT_DEDUP_WINDOW_SECONDS)
                return alert

        alert = Alert(
            rule_id=rule.id,
            rule_name=rule.name,
            mitre_technique_id=rule.mitre_technique_id,
            mitre_technique_name=rule.mitre_technique_name,
            severity=severity,
            status=AlertStatus.NEW,
            source_ip=source_ip,
            target=target,
            title=title,
            description=description,
            related_event_ids=",".join(str(i) for i in related_event_ids),
            event_count=occurrence_count,
            dedup_key=dedup_key,
            first_seen=now,
            last_seen=now,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        redis_safe_setex(dedup_key, settings.ALERT_DEDUP_WINDOW_SECONDS, alert.id)

        if severity == Severity.CRITICAL:
            dispatch_critical_notification(alert)

        return alert