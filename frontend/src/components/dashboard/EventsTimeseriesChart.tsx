import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { format } from "date-fns";
import type { TimeseriesBucket } from "../../types";

export function EventsTimeseriesChart({ buckets }: { buckets: TimeseriesBucket[] }) {
  const data = buckets.map((b) => ({
    ts: b.timestamp,
    label: format(new Date(b.timestamp), "HH:mm"),
    count: b.count,
  }));

  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display font-semibold text-sm">Event Volume</h3>
        <span className="text-xs font-mono text-ink-faint">last 24h</span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="eventsFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2DD4BF" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#2DD4BF" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1A2530" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: "#5B6E80", fontSize: 11, fontFamily: "JetBrains Mono" }}
            axisLine={{ stroke: "#22303D" }}
            tickLine={false}
            minTickGap={40}
          />
          <YAxis
            tick={{ fill: "#5B6E80", fontSize: 11, fontFamily: "JetBrains Mono" }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip
            contentStyle={{
              background: "#0D1319",
              border: "1px solid #22303D",
              borderRadius: 8,
              fontSize: 12,
              fontFamily: "JetBrains Mono",
            }}
            labelStyle={{ color: "#8CA0B3" }}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#2DD4BF"
            strokeWidth={2}
            fill="url(#eventsFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
