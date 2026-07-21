import clsx from "clsx";
import type { Severity } from "../types";

const SEVERITY_STYLES: Record<Severity, string> = {
  info: "bg-sev-info/10 text-sev-info border-sev-info/30",
  low: "bg-sev-low/10 text-sev-low border-sev-low/30",
  medium: "bg-sev-medium/10 text-sev-medium border-sev-medium/30",
  high: "bg-sev-high/10 text-sev-high border-sev-high/30",
  critical: "bg-sev-critical/10 text-sev-critical border-sev-critical/30",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span className={clsx("badge border", SEVERITY_STYLES[severity])}>
      {severity === "critical" && <span className="h-1.5 w-1.5 rounded-full bg-sev-critical animate-pulse" />}
      {severity.toUpperCase()}
    </span>
  );
}
