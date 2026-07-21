import logging
import smtplib
from email.mime.text import MIMEText

import httpx

from app.core.config import settings
from app.models.alert import Alert

logger = logging.getLogger("sentinelview.notifications")


def _send_webhook(alert: Alert) -> None:
    if not settings.ALERT_WEBHOOK_URL:
        return
    payload = {
        "text": (
            f":rotating_light: *CRITICAL ALERT* — {alert.title}\n"
            f"Rule: {alert.rule_name} ({alert.mitre_technique_id or 'n/a'})\n"
            f"Source IP: {alert.source_ip or 'n/a'}  Target: {alert.target or 'n/a'}\n"
            f"{alert.description}"
        )
    }
    try:
        httpx.post(settings.ALERT_WEBHOOK_URL, json=payload, timeout=5.0)
    except httpx.HTTPError as exc:
        logger.warning("Webhook dispatch failed: %s", exc)


def _send_email(alert: Alert) -> None:
    if not (settings.SMTP_HOST and settings.ALERT_EMAIL_TO and settings.ALERT_EMAIL_FROM):
        return
    body = (
        f"Rule: {alert.rule_name}\nMITRE: {alert.mitre_technique_id}\n"
        f"Source IP: {alert.source_ip}\nTarget: {alert.target}\n\n{alert.description}"
    )
    msg = MIMEText(body)
    msg["Subject"] = f"[SentinelView] CRITICAL: {alert.title}"
    msg["From"] = settings.ALERT_EMAIL_FROM
    msg["To"] = settings.ALERT_EMAIL_TO

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5) as server:
            server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.ALERT_EMAIL_FROM, [settings.ALERT_EMAIL_TO], msg.as_string())
    except (smtplib.SMTPException, OSError) as exc:
        logger.warning("Email dispatch failed: %s", exc)


def dispatch_critical_notification(alert: Alert) -> None:
    """Best-effort fan-out; failures are logged, never raised, so a broken
    webhook/SMTP config can't take down the ingestion pipeline."""
    _send_webhook(alert)
    _send_email(alert)
