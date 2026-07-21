import type { ReactNode } from "react";
import clsx from "clsx";

export function StatCard({
  label,
  value,
  sub,
  icon,
  accent,
}: {
  label: string;
  value: ReactNode;
  sub?: string;
  icon?: ReactNode;
  accent?: "signal" | "critical" | "high" | "default";
}) {
  const accentColor = {
    signal: "text-signal",
    critical: "text-sev-critical",
    high: "text-sev-high",
    default: "text-ink",
  }[accent ?? "default"];

  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between">
        <span className="text-xs font-mono uppercase tracking-wide text-ink-faint">{label}</span>
        {icon && <span className="text-ink-faint">{icon}</span>}
      </div>
      <div className={clsx("mt-2 font-display text-2xl font-semibold", accentColor)}>{value}</div>
      {sub && <div className="mt-1 text-xs text-ink-muted">{sub}</div>}
    </div>
  );
}
