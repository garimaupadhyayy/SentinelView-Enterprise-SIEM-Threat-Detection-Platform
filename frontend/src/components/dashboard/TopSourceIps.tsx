import type { DashboardSummary } from "../../types";

export function TopSourceIps({ summary }: { summary: DashboardSummary }) {
  const max = Math.max(1, ...summary.top_source_ips.map((i) => i.count));

  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display font-semibold text-sm">Top Source IPs</h3>
        <span className="text-xs font-mono text-ink-faint">
          window: {summary.window_minutes}m
        </span>
      </div>
      {summary.top_source_ips.length === 0 ? (
        <p className="text-sm text-ink-faint py-6 text-center">No activity in this window.</p>
      ) : (
        <div className="space-y-2">
          {summary.top_source_ips.map((ip) => (
            <div key={ip.source_ip} className="flex items-center gap-3">
              <span className="font-mono text-xs w-32 shrink-0 text-ink-muted truncate">
                {ip.source_ip}
              </span>
              <div className="flex-1 h-2 bg-base-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-signal/70 rounded-full"
                  style={{ width: `${(ip.count / max) * 100}%` }}
                />
              </div>
              <span className="font-mono text-xs w-10 text-right text-ink">{ip.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
