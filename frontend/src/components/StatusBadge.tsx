import clsx from "clsx";
import type { AlertStatus } from "../types";

const STATUS_STYLES: Record<AlertStatus, string> = {
  new: "bg-signal/10 text-signal border-signal/30",
  investigating: "bg-sev-medium/10 text-sev-medium border-sev-medium/30",
  resolved: "bg-ink-faint/10 text-ink-muted border-line",
  false_positive: "bg-ink-faint/10 text-ink-faint border-line line-through",
};

const STATUS_LABELS: Record<AlertStatus, string> = {
  new: "New",
  investigating: "Investigating",
  resolved: "Resolved",
  false_positive: "False Positive",
};

export function StatusBadge({ status }: { status: AlertStatus }) {
  return <span className={clsx("badge border", STATUS_STYLES[status])}>{STATUS_LABELS[status]}</span>;
}
