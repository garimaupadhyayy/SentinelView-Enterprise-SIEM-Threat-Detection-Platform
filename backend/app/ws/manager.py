import asyncio
import json

from fastapi import WebSocket


class ConnectionManager:
    """
    Simple in-memory pub/sub for the dashboard's live tail and alert feed.
    Single-node deployment (per the spec, no distributed architecture needed),
    so an in-process broadcast list is sufficient -- no external message
    broker required.
    """

    def __init__(self):
        self._event_sockets: set[WebSocket] = set()
        self._alert_sockets: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect_events(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._event_sockets.add(ws)

    async def connect_alerts(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._alert_sockets.add(ws)

    async def disconnect_events(self, ws: WebSocket) -> None:
        async with self._lock:
            self._event_sockets.discard(ws)

    async def disconnect_alerts(self, ws: WebSocket) -> None:
        async with self._lock:
            self._alert_sockets.discard(ws)

    async def broadcast_event(self, payload: dict) -> None:
        dead = []
        for ws in list(self._event_sockets):
            try:
                await ws.send_text(json.dumps(payload, default=str))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._event_sockets.discard(ws)

    async def broadcast_alert(self, payload: dict) -> None:
        dead = []
        for ws in list(self._alert_sockets):
            try:
                await ws.send_text(json.dumps(payload, default=str))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._alert_sockets.discard(ws)


manager = ConnectionManager()
