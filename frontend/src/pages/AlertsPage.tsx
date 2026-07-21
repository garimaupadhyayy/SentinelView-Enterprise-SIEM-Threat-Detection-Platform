import { useCallback, useEffect, useState } from "react";
import { formatDistanceToNowStrict } from "date-fns";
import { FileDown, FileText, X } from "lucide-react";
import {
  downloadCsvReport,
  downloadPdfReport,
  fetchAlertEvents,
  fetchAlerts,
  updateAlertStatus,
} from "../api/endpoints";
import type { Alert, AlertStatus, EventRecord, Severity } from "../types";
import { SeverityBadge } from "../components/SeverityBadge";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../context/AuthContext";

const STATUS_OPTIONS: { value: AlertStatus | ""; label: string }[] = [
  { value: "", label: "All statuses" },
  { value: "new", label: "New" },
  { value: "investigating", label: "Investigating" },
  { value: "resolved", label: "Resolved" },
  { value: "false_positive", label: "False Positive" },
];

const SEVERITY_OPTIONS: { value: Severity | ""; label: string }[] = [
  { value: "", label: "All severities" },
  { value: "critical", label: "Critical" },
  { value: "high", label: "High" },
  { value: "medium", label: "Medium" },
  { value: "low", label: "Low" },
  { value: "info", label: "Info" },
];

export function AlertsPage() {
  const { hasRole } = useAuth();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [severity, setSeverity] = useState<Severity | "">("");
  const [status, setStatus] = useState<AlertStatus | "">("");
  const [selected, setSelected] = useState<Alert | null>(null);
  const [selectedEvents, setSelectedEvents] = useState<EventRecord[]>([]);
  const canTriage = hasRole("admin", "analyst");

  const load = useCallback(async () => {
    const data = await fetchAlerts({
      severity: severity || undefined,
      status: status || undefined,
      limit: 100,
    });
    setAlerts(data);
  }, [severity, status]);

  useEffect(() => {
    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, [load]);

  async function openAlert(a: Alert) {
    setSelected(a);
    const events = await fetchAlertEvents(a.id);
    setSelectedEvents(events);
  }

  async function handleStatusChange(a: Alert, newStatus: AlertStatus) {
    const updated = await updateAlertStatus(a.id, newStatus);
    setAlerts((prev) => prev.map((x) => (x.id === updated.id ? updated : x)));
    if (selected?.id === updated.id) setSelected(updated);
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Alert Triage</h1>
          <p className="text-sm text-ink-muted mt-1">
            {alerts.length} alert{alerts.length === 1 ? "" : "s"} matching current filters.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => downloadCsvReport({})}
            className="flex items-center gap-1.5 text-xs font-mono border border-line rounded-md px-3 py-1.5 text-ink-muted hover:text-ink hover:border-signal/40 transition-colors"
          >
            <FileDown className="h-3.5 w-3.5" /> CSV
          </button>
          <button
            onClick={() => downloadPdfReport({})}
            className="flex items-center gap-1.5 text-xs font-mono border border-line rounded-md px-3 py-1.5 text-ink-muted hover:text-ink hover:border-signal/40 transition-colors"
          >
            <FileText className="h-3.5 w-3.5" /> PDF
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <select
          value={severity}
          onChange={(e) => setSeverity(e.target.value as Severity | "")}
          className="bg-base-800 border border-line rounded-md px-2.5 py-1.5 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-signal/40"
        >
          {SEVERITY_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as AlertStatus | "")}
          className="bg-base-800 border border-line rounded-md px-2.5 py-1.5 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-signal/40"
        >
          {STATUS_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      <div className="panel overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-base-800/60 text-xs font-mono uppercase text-ink-faint">
            <tr>
              <th className="text-left px-4 py-2.5 font-medium">Severity</th>
              <th className="text-left px-4 py-2.5 font-medium">Title</th>
              <th className="text-left px-4 py-2.5 font-medium">MITRE</th>
              <th className="text-left px-4 py-2.5 font-medium">Source IP</th>
              <th className="text-left px-4 py-2.5 font-medium">Status</th>
              <th className="text-left px-4 py-2.5 font-medium">Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((a) => (
              <tr
                key={a.id}
                onClick={() => openAlert(a)}
                className="border-t border-line hover:bg-base-800/40 cursor-pointer transition-colors"
              >
                <td className="px-4 py-2.5">
                  <SeverityBadge severity={a.severity} />
                </td>
                <td className="px-4 py-2.5 max-w-xs truncate">{a.title}</td>
                <td className="px-4 py-2.5 font-mono text-xs text-ink-muted">
                  {a.mitre_technique_id ?? "-"}
                </td>
                <td className="px-4 py-2.5 font-mono text-xs text-ink-muted">
                  {a.source_ip ?? "-"}
                </td>
                <td className="px-4 py-2.5">
                  <StatusBadge status={a.status} />
                </td>
                <td className="px-4 py-2.5 font-mono text-xs text-ink-faint">
                  {formatDistanceToNowStrict(new Date(a.last_seen), { addSuffix: true })}
                </td>
              </tr>
            ))}
            {alerts.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-10 text-center text-ink-faint text-sm">
                  No alerts match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {selected && (
        <div className="fixed inset-0 bg-black/50 flex justify-end z-50" onClick={() => setSelected(null)}>
          <div
            className="w-full max-w-lg bg-base-900 border-l border-line h-full overflow-y-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <SeverityBadge severity={selected.severity} />
                <h2 className="font-display font-semibold text-lg mt-2">{selected.title}</h2>
              </div>
              <button onClick={() => setSelected(null)} className="text-ink-faint hover:text-ink">
                <X className="h-5 w-5" />
              </button>
            </div>

            <p className="text-sm text-ink-muted mb-4">{selected.description}</p>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono mb-6">
              <div className="panel p-3">
                <div className="text-ink-faint">MITRE Technique</div>
                <div className="text-ink mt-1">
                  {selected.mitre_technique_id} — {selected.mitre_technique_name}
                </div>
              </div>
              <div className="panel p-3">
                <div className="text-ink-faint">Source IP</div>
                <div className="text-ink mt-1">{selected.source_ip ?? "-"}</div>
              </div>
              <div className="panel p-3">
                <div className="text-ink-faint">Target</div>
                <div className="text-ink mt-1">{selected.target ?? "-"}</div>
              </div>
              <div className="panel p-3">
                <div className="text-ink-faint">Event Count</div>
                <div className="text-ink mt-1">{selected.event_count}</div>
              </div>
            </div>

            {canTriage && (
              <div className="mb-6">
                <label className="text-xs font-mono uppercase text-ink-faint">Update Status</label>
                <select
                  value={selected.status}
                  onChange={(e) => handleStatusChange(selected, e.target.value as AlertStatus)}
                  className="w-full mt-1.5 bg-base-800 border border-line rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/40"
                >
                  <option value="new">New</option>
                  <option value="investigating">Investigating</option>
                  <option value="resolved">Resolved</option>
                  <option value="false_positive">False Positive</option>
                </select>
              </div>
            )}

            <div className="flex gap-2 mb-6">
              <button
                onClick={() => downloadCsvReport({ alert_id: selected.id })}
                className="flex items-center gap-1.5 text-xs font-mono border border-line rounded-md px-3 py-1.5 text-ink-muted hover:text-ink hover:border-signal/40"
              >
                <FileDown className="h-3.5 w-3.5" /> Export CSV
              </button>
              <button
                onClick={() => downloadPdfReport({ alert_id: selected.id })}
                className="flex items-center gap-1.5 text-xs font-mono border border-line rounded-md px-3 py-1.5 text-ink-muted hover:text-ink hover:border-signal/40"
              >
                <FileText className="h-3.5 w-3.5" /> Export PDF
              </button>
            </div>

            <h3 className="font-display font-semibold text-sm mb-2">
              Related Events ({selectedEvents.length})
            </h3>
            <div className="space-y-1.5 font-mono text-xs max-h-80 overflow-y-auto">
              {selectedEvents.map((e) => (
                <div key={e.id} className="panel p-2">
                  <div className="flex items-center gap-2 text-ink-faint">
                    <span>{new Date(e.timestamp).toLocaleString()}</span>
                    <SeverityBadge severity={e.severity} />
                  </div>
                  <div className="text-ink-muted mt-1 truncate">{e.raw_message}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
