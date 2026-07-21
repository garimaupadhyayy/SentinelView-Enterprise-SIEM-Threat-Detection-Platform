from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.event import Event
from app.models.rule import DetectionRule
from app.services.alert_service import AlertService
from app.services import geoip_service


class CorrelationEngine:
    """
    Rule-based (explicitly NOT ML) correlation engine. On every new event,
    evaluate_event() pulls all *enabled* rules from the DB and dispatches to
    a handler keyed by rule_type. Handlers look at a short recent window of
    events (queried straight from MySQL, which is indexed on source_ip +
    timestamp for exactly this) and decide whether the pattern's threshold
    is met. This keeps detection logic fully explainable: every alert can
    point at the exact rule config and events that produced it.

    Adding a new rule of an *existing* type is just a new DetectionRule row
    (the "custom rule builder" in the UI). Adding a genuinely new detection
    *strategy* means adding one function here and registering it in
    RULE_HANDLERS -- everything else (storage, API, UI) is generic.
    """

    def __init__(self, db: Session):
        self.db = db
        self.alert_service = AlertService(db)

    def _enabled_rules(self, rule_type: str | None = None) -> list[DetectionRule]:
        q = self.db.query(DetectionRule).filter(DetectionRule.enabled.is_(True))
        if rule_type:
            q = q.filter(DetectionRule.rule_type == rule_type)
        return q.all()

    def evaluate_event(self, event: Event) -> list[Alert]:
        alerts: list[Alert] = []
        for rule in self._enabled_rules():
            handler = RULE_HANDLERS.get(rule.rule_type)
            if not handler:
                continue
            alert = handler(self, event, rule)
            if alert:
                alerts.append(alert)
        return alerts

    # ---- rule handlers -------------------------------------------------

    def _handle_brute_force(self, event: Event, rule: DetectionRule) -> Alert | None:
        cfg = rule.config or {}
        event_types = cfg.get("event_types", ["auth_failure"])
        window = cfg.get("window_seconds", 300)
        threshold = cfg.get("threshold", 5)

        if event.event_type not in event_types or not event.source_ip:
            return None

        window_start = event.timestamp - timedelta(seconds=window)
        count = (
            self.db.query(Event)
            .filter(
                Event.source_ip == event.source_ip,
                Event.event_type.in_(event_types),
                Event.timestamp >= window_start,
                Event.timestamp <= event.timestamp,
            )
            .count()
        )
        if count < threshold:
            return None

        recent_ids = [
            e.id
            for e in self.db.query(Event.id)
            .filter(
                Event.source_ip == event.source_ip,
                Event.event_type.in_(event_types),
                Event.timestamp >= window_start,
                Event.timestamp <= event.timestamp,
            )
            .order_by(Event.timestamp.desc())
            .limit(50)
            .all()
        ]

        return self.alert_service.raise_alert(
            rule=rule,
            title=f"Brute force login attempt from {event.source_ip}",
            description=(
                f"{count} failed authentication attempts from {event.source_ip} "
                f"within the last {window} seconds (threshold: {threshold})."
            ),
            source_ip=event.source_ip,
            # Deliberately dedup by source IP only (target=None), not per
            # targeted username: an attacker rotating through root/admin/test
            # is still one brute-force campaign and should collapse into a
            # single alert, not fragment into one per username tried.
            target=None,
            related_event_ids=recent_ids,
            occurrence_count=count,
        )

    def _handle_port_scan(self, event: Event, rule: DetectionRule) -> Alert | None:
        cfg = rule.config or {}
        window = cfg.get("window_seconds", 60)
        threshold = cfg.get("distinct_ports_threshold", 10)

        if not event.source_ip or event.port is None:
            return None

        window_start = event.timestamp - timedelta(seconds=window)
        distinct_ports = (
            self.db.query(Event.port)
            .filter(
                Event.source_ip == event.source_ip,
                Event.port.isnot(None),
                Event.timestamp >= window_start,
                Event.timestamp <= event.timestamp,
            )
            .distinct()
            .count()
        )
        if distinct_ports < threshold:
            return None

        recent_ids = [
            e.id
            for e in self.db.query(Event.id)
            .filter(
                Event.source_ip == event.source_ip,
                Event.timestamp >= window_start,
                Event.timestamp <= event.timestamp,
            )
            .order_by(Event.timestamp.desc())
            .limit(100)
            .all()
        ]

        return self.alert_service.raise_alert(
            rule=rule,
            title=f"Port scan detected from {event.source_ip}",
            description=(
                f"{event.source_ip} touched {distinct_ports} distinct ports "
                f"within {window} seconds (threshold: {threshold}) -- consistent "
                f"with network reconnaissance."
            ),
            source_ip=event.source_ip,
            target=event.destination_ip,
            related_event_ids=recent_ids,
            occurrence_count=distinct_ports,
        )

    def _handle_impossible_travel(self, event: Event, rule: DetectionRule) -> Alert | None:
        cfg = rule.config or {}
        window = cfg.get("window_seconds", 3600)
        min_kmh = cfg.get("min_plausible_kmh", 900)

        if event.event_type != "auth_success" or not event.user or not event.source_ip:
            return None

        window_start = event.timestamp - timedelta(seconds=window)
        prior = (
            self.db.query(Event)
            .filter(
                Event.user == event.user,
                Event.event_type == "auth_success",
                Event.source_ip.isnot(None),
                Event.source_ip != event.source_ip,
                Event.timestamp >= window_start,
                Event.timestamp < event.timestamp,
            )
            .order_by(Event.timestamp.desc())
            .first()
        )
        if not prior:
            return None

        loc_a = geoip_service.lookup_ip(prior.source_ip)
        loc_b = geoip_service.lookup_ip(event.source_ip)
        if not loc_a or not loc_b:
            return None  # can't compute distance without both locations

        distance_km = geoip_service.haversine_km(loc_a["lat"], loc_a["lon"], loc_b["lat"], loc_b["lon"])
        hours = max((event.timestamp - prior.timestamp).total_seconds() / 3600, 1 / 60)
        required_kmh = distance_km / hours

        if required_kmh < min_kmh or distance_km < 200:
            return None

        return self.alert_service.raise_alert(
            rule=rule,
            title=f"Impossible travel for user '{event.user}'",
            description=(
                f"User '{event.user}' logged in from {loc_a['city']}, {loc_a['country']} "
                f"and then from {loc_b['city']}, {loc_b['country']} "
                f"({distance_km:.0f} km apart) only {hours:.2f}h later -- implies "
                f"~{required_kmh:.0f} km/h travel speed."
            ),
            source_ip=event.source_ip,
            target=event.user,
            related_event_ids=[prior.id, event.id],
            occurrence_count=2,
        )

    def _handle_priv_escalation(self, event: Event, rule: DetectionRule) -> Alert | None:
        cfg = rule.config or {}
        window = cfg.get("window_seconds", 600)
        threshold = cfg.get("threshold", 5)

        if event.event_type != "privilege_command" or not event.user:
            return None

        window_start = event.timestamp - timedelta(seconds=window)
        count = (
            self.db.query(Event)
            .filter(
                Event.user == event.user,
                Event.event_type == "privilege_command",
                Event.timestamp >= window_start,
                Event.timestamp <= event.timestamp,
            )
            .count()
        )
        if count < threshold:
            return None

        recent_ids = [
            e.id
            for e in self.db.query(Event.id)
            .filter(
                Event.user == event.user,
                Event.event_type == "privilege_command",
                Event.timestamp >= window_start,
                Event.timestamp <= event.timestamp,
            )
            .order_by(Event.timestamp.desc())
            .limit(50)
            .all()
        ]

        return self.alert_service.raise_alert(
            rule=rule,
            title=f"Privilege escalation spike for user '{event.user}'",
            description=(
                f"User '{event.user}' issued {count} sudo/su commands within "
                f"{window} seconds (threshold: {threshold}) -- unusual relative "
                f"to normal account behavior."
            ),
            source_ip=event.source_ip,
            target=event.user,
            related_event_ids=recent_ids,
            occurrence_count=count,
        )

    def _handle_web_attack_signature(self, event: Event, rule: DetectionRule) -> Alert | None:
        cfg = rule.config or {}
        event_types = cfg.get("event_types", ["sqli_signature", "xss_signature"])

        if event.event_type not in event_types:
            return None

        attack_kind = "SQL injection" if event.event_type == "sqli_signature" else "XSS"

        return self.alert_service.raise_alert(
            rule=rule,
            title=f"{attack_kind} attempt from {event.source_ip}",
            description=(
                f"Request path matched a known {attack_kind} signature: "
                f"{(event.url_path or '')[:200]}"
            ),
            source_ip=event.source_ip,
            target=event.url_path,
            related_event_ids=[event.id],
            occurrence_count=1,
        )


RULE_HANDLERS = {
    "brute_force": CorrelationEngine._handle_brute_force,
    "port_scan": CorrelationEngine._handle_port_scan,
    "impossible_travel": CorrelationEngine._handle_impossible_travel,
    "priv_escalation": CorrelationEngine._handle_priv_escalation,
    "web_attack_signature": CorrelationEngine._handle_web_attack_signature,
}
