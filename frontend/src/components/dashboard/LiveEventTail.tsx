import { formatDistanceToNowStrict } from "date-fns";
import { useLiveStream } from "../../hooks/useLiveStream";
import type { EventRecord } from "../../types";
import { SeverityBadge } from "../SeverityBadge";

export function LiveEventTail() {
  const { items, connected } = useLiveStream<EventRecord>("/ws/events", 50);

  return (
    <div className="panel p-4 flex flex-col h-full">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display font-semibold text-sm">Live Event Tail</h3>
        <span
          className={
            "text-xs font-mono flex items-center gap-1.5 " +
            (connected ? "text-signal" : "text-ink-faint")
          }
        >
          <span
            className={
              "h-1.5 w-1.5 rounded-full " + (connected ? "bg-signal animate-pulse" : "bg-ink-faint")
            }
          />
          {connected ? "streaming" : "offline"}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-1.5 font-mono text-xs pr-1 max-h-[420px]">
        {items.length === 0 && (
          <p className="text-ink-faint py-6 text-center font-sans">
            Waiting for events… push logs via the API or upload a file to see them here live.
          </p>
        )}
        {items.map((e) => (
          <div
            key={e.id}
            className="flex items-center gap-2 border-b border-line/60 pb-1.5 last:border-0"
          >
            <span className="text-ink-faint shrink-0 w-16">
              {formatDistanceToNowStrict(new Date(e.timestamp), { addSuffix: false })}
            </span>
            <SeverityBadge severity={e.severity} />
            <span className="text-ink-muted shrink-0">{e.source_ip ?? "-"}</span>
            <span className="text-signal shrink-0">{e.event_type}</span>
            <span className="text-ink-faint truncate">{e.raw_message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
