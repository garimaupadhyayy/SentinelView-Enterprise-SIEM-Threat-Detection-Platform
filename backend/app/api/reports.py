import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_any_role
from app.models.alert import Alert
from app.models.event import Event
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])


def _fetch_alerts(db: Session, alert_id: int | None, start: datetime | None, end: datetime | None) -> list[Alert]:
    if alert_id:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Alert not found")
        return [alert]

    query = db.query(Alert)
    if start:
        query = query.filter(Alert.created_at >= start)
    if end:
        query = query.filter(Alert.created_at <= end)
    return query.order_by(Alert.created_at.desc()).limit(500).all()


@router.get("/incident.csv")
def export_csv(
    alert_id: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    alerts = _fetch_alerts(db, alert_id, start, end)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "id", "title", "rule_name", "mitre_technique_id", "severity", "status",
            "source_ip", "target", "event_count", "first_seen", "last_seen", "description",
        ]
    )
    for a in alerts:
        writer.writerow(
            [
                a.id, a.title, a.rule_name, a.mitre_technique_id, a.severity.value, a.status.value,
                a.source_ip, a.target, a.event_count, a.first_seen, a.last_seen, a.description,
            ]
        )
    buf.seek(0)
    filename = f"sentinelview_incident_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/incident.pdf")
def export_pdf(
    alert_id: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_any_role),
):
    alerts = _fetch_alerts(db, alert_id, start, end)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("SentinelView Incident Report", styles["Title"]),
        Paragraph(f"Generated: {datetime.utcnow().isoformat()} UTC", styles["Normal"]),
        Spacer(1, 16),
    ]

    for a in alerts:
        story.append(Paragraph(f"Alert #{a.id}: {a.title}", styles["Heading2"]))
        story.append(Paragraph(a.description, styles["Normal"]))
        story.append(Spacer(1, 6))

        related_ids = [int(i) for i in (a.related_event_ids or "").split(",") if i][:20]
        events = (
            db.query(Event).filter(Event.id.in_(related_ids)).order_by(Event.timestamp).all()
            if related_ids
            else []
        )

        table_data = [["Field", "Value"]]
        table_data += [
            ["Rule", a.rule_name],
            ["MITRE Technique", f"{a.mitre_technique_id or '-'} ({a.mitre_technique_name or '-'})"],
            ["Severity", a.severity.value],
            ["Status", a.status.value],
            ["Source IP", a.source_ip or "-"],
            ["Target", a.target or "-"],
            ["Event Count", str(a.event_count)],
            ["First Seen", str(a.first_seen)],
            ["Last Seen", str(a.last_seen)],
            ["Related Events Shown", str(len(events))],
        ]
        t = Table(table_data, colWidths=[140, 340])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 16))

    if not alerts:
        story.append(Paragraph("No alerts matched the given filters.", styles["Normal"]))

    doc.build(story)
    buf.seek(0)

    filename = f"sentinelview_incident_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
