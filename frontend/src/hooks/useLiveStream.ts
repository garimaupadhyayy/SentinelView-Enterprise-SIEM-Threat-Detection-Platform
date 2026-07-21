import { useEffect, useRef, useState } from "react";
import { WS_BASE } from "../api/client";

/**
 * Subscribes to a SentinelView websocket endpoint (/ws/events or /ws/alerts)
 * and keeps a rolling buffer of the most recent `maxItems` messages.
 * Reconnects automatically with backoff if the socket drops -- dashboards
 * are meant to stay open for hours in a SOC, so this can't just give up.
 */
export function useLiveStream<T>(path: "/ws/events" | "/ws/alerts", maxItems = 100) {
  const [items, setItems] = useState<T[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const retryDelay = useRef(1000);

  useEffect(() => {
    let cancelled = false;
    let reconnectTimer: ReturnType<typeof setTimeout>;

    function connect() {
      if (cancelled) return;
      const token = localStorage.getItem("sv_access_token") || "";
      const ws = new WebSocket(`${WS_BASE}${path}?token=${encodeURIComponent(token)}`);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        retryDelay.current = 1000;
      };

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload?.data) {
            setItems((prev) => [payload.data as T, ...prev].slice(0, maxItems));
          }
        } catch {
          // ignore malformed frames
        }
      };

      ws.onclose = () => {
        setConnected(false);
        if (!cancelled) {
          reconnectTimer = setTimeout(connect, retryDelay.current);
          retryDelay.current = Math.min(retryDelay.current * 1.5, 15000);
        }
      };

      ws.onerror = () => {
        ws.close();
      };
    }

    connect();

    return () => {
      cancelled = true;
      clearTimeout(reconnectTimer);
      wsRef.current?.close();
    };
  }, [path, maxItems]);

  return { items, connected };
}
