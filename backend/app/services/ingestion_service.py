from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.ingestion import IngestionSource
from app.schemas.event import NormalizedEventIn
from app.services.correlation_engine import CorrelationEngine


class IngestionService:
    """
    Single choke point for getting normalized events into MySQL and handed
    off to the correlation engine. Both the file-upload endpoint and the
    REST push endpoint (and, transitively, the log-shipper agent) funnel
    through here so detection logic only has to live in one place.
    """

    def __init__(self, db: Session):
        self.db = db
        self.engine = CorrelationEngine(db)
        self.last_alerts: list = []

    def ingest_events(
        self, events: list[NormalizedEventIn], source_name: str = "unknown"
    ) -> list[Event]:
        db_events: list[Event] = []
        for e in events:
            db_event = Event(**e.model_dump())
            self.db.add(db_event)
            db_events.append(db_event)

        self.db.commit()
        for db_event in db_events:
            self.db.refresh(db_event)

        self._touch_source(source_name)

        # Run correlation synchronously for MVP simplicity/explainability.
        # Each new event is evaluated against all enabled rules immediately.
        # Alerts produced are stashed on self.last_alerts so the (async) API
        # layer can broadcast them over the /ws/alerts socket after we return.
        self.last_alerts = []
        for db_event in db_events:
            self.last_alerts.extend(self.engine.evaluate_event(db_event))

        return db_events

    def _touch_source(self, source_name: str) -> None:
        source = self.db.query(IngestionSource).filter_by(name=source_name).first()
        now = datetime.now(timezone.utc)
        if source:
            source.last_seen = now
        else:
            source = IngestionSource(name=source_name, source_type="mixed", last_seen=now)
            self.db.add(source)
        self.db.commit()
