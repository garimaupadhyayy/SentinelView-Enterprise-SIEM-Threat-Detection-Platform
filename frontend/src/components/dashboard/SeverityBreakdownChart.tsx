import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell } from "recharts";
import type { DashboardSummary, Severity } from "../../types";

const ORDER: Severity[] = ["info", "low", "medium", "high", "critical"];
const COLORS: Record<Severity, string> = {
  info: "#5B8DEF",
  low: "#3FB6C7",
  medium: "#E5B93E",
  high: "#F2924A",
  critical: "#EF5A5A",
};

export function SeverityBreakdownChart({ summary }: { summary: DashboardSummary }) {
  const data = ORDER.map((sev) => ({
    severity: sev,
    count: summary.alert_counts_by_severity[sev] ?? 0,
  }));

  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display font-semibold text-sm">Alerts by Severity</h3>
        <span className="text-xs font-mono text-ink-faint">{summary.total_alerts} total</span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
          <CartesianGrid stroke="#1A2530" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="severity"
            tick={{ fill: "#5B6E80", fontSize: 11, fontFamily: "JetBrains Mono" }}
            axisLine={{ stroke: "#22303D" }}
            tickLine={false}
            tickFormatter={(v) => v.toUpperCase()}
          />
          <YAxis
            tick={{ fill: "#5B6E80", fontSize: 11, fontFamily: "JetBrains Mono" }}
            axisLine={false}
            tickLine={false}
            width={30}
            allowDecimals={false}
          />
          <Tooltip
            contentStyle={{
              background: "#0D1319",
              border: "1px solid #22303D",
              borderRadius: 8,
              fontSize: 12,
              fontFamily: "JetBrains Mono",
            }}
            cursor={{ fill: "rgba(255,255,255,0.03)" }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((d) => (
              <Cell key={d.severity} fill={COLORS[d.severity]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
