from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.db import SessionLocal
from app.core.security import decode_token
from app.models.user import User
from app.ws.manager import manager

router = APIRouter(tags=["websocket"])


def _authorized(token: str | None) -> bool:
    """Websockets can't send an Authorization header from the browser, so
    the frontend passes the JWT as ?token=... instead. Any authenticated,
    active user (any role) may watch the live feed -- it's read-only."""
    if not token:
        return False
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return False
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == payload.get("sub")).first()
        return bool(user and user.is_active)
    finally:
        db.close()


@router.websocket("/ws/events")
async def ws_events(websocket: WebSocket, token: str | None = Query(default=None)):
    """Live tail of every normalized event as it's ingested."""
    if not _authorized(token):
        await websocket.close(code=4401)
        return
    await manager.connect_events(websocket)
    try:
        while True:
            # We don't expect client -> server messages, but need to keep
            # the receive loop alive to detect disconnects.
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_events(websocket)


@router.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket, token: str | None = Query(default=None)):
    """Live stream of new/updated alerts as the correlation engine fires."""
    if not _authorized(token):
        await websocket.close(code=4401)
        return
    await manager.connect_alerts(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_alerts(websocket)
