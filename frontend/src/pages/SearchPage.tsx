import { useCallback, useState, type FormEvent } from "react";
import { Search as SearchIcon } from "lucide-react";
import { searchEvents } from "../api/endpoints";
import type { EventRecord, Severity, SourceType } from "../types";
import { SeverityBadge } from "../components/SeverityBadge";

const SOURCE_TYPE_OPTIONS: { value: SourceType | ""; label: string }[] = [
  { value: "", label: "All source types" },
  { value: "ssh_auth", label: "SSH Auth" },
  { value: "web_access", label: "Web Access" },
  { value: "firewall", label: "Firewall" },
];

const SEVERITY_OPTIONS: { value: Severity | ""; label: string }[] = [
  { value: "", label: "All severities" },
  { value: "critical", label: "Critical" },
  { value: "high", label: "High" },
  { value: "medium", label: "Medium" },
  { value: "low", label: "Low" },
  { value: "info", label: "Info" },
];

export function SearchPage() {
  const [q, setQ] = useState("");
  const [sourceIp, setSourceIp] = useState("");
  const [severity, setSeverity] = useState<Severity | "">("");
  const [sourceType, setSourceType] = useState<SourceType | "">("");
  const [results, setResults] = useState<EventRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const runSearch = useCallback(
    async (e?: FormEvent) => {
      e?.preventDefault();
      setLoading(true);
      try {
        const data = await searchEvents({
          q: q || undefined,
          source_ip: sourceIp || undefined,
          severity: severity || undefined,
          source_type: sourceType || undefined,
          limit: 200,
        });
        setResults(data);
        setSearched(true);
      } finally {
        setLoading(false);
      }
    },
    [q, sourceIp, severity, sourceType]
  );

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="font-display text-2xl font-semibold">Log Search</h1>
        <p className="text-sm text-ink-muted mt-1">
          Full-text and filtered search across every normalized event.
        </p>
      </div>

      <form onSubmit={runSearch} className="panel p-4 space-y-3">
        <div className="relative">
          <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-faint" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search raw log messages / URL paths…"
            className="w-full bg-base-800 border border-line rounded-md pl-9 pr-3 py-2.5 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-signal/40 focus:border-signal/50"
          />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <input
            value={sourceIp}
            onChange={(e) => setSourceIp(e.target.value)}
            placeholder="source_ip"
            className="bg-base-800 border border-line rounded-md px-3 py-1.5 text-xs font-mono w-40 focus:outline-none focus:ring-2 focus:ring-signal/40"
          />
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
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value as SourceType | "")}
            className="bg-base-800 border border-line rounded-md px-2.5 py-1.5 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-signal/40"
          >
            {SOURCE_TYPE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <button
            type="submit"
            className="bg-signal text-base-950 font-medium rounded-md px-4 py-1.5 text-xs hover:bg-signal-glow transition-colors ml-auto"
          >
            {loading ? "Searching…" : "Search"}
          </button>
        </div>
      </form>

      <div className="panel overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-base-800/60 text-xs font-mono uppercase text-ink-faint">
            <tr>
              <th className="text-left px-4 py-2.5 font-medium">Timestamp</th>
              <th className="text-left px-4 py-2.5 font-medium">Severity</th>
              <th className="text-left px-4 py-2.5 font-medium">Source</th>
              <th className="text-left px-4 py-2.5 font-medium">Event Type</th>
              <th className="text-left px-4 py-2.5 font-medium">Message</th>
            </tr>
          </thead>
          <tbody>
            {results.map((e) => (
              <tr key={e.id} className="border-t border-line hover:bg-base-800/40">
                <td className="px-4 py-2 font-mono text-xs text-ink-faint whitespace-nowrap">
                  {new Date(e.timestamp).toLocaleString()}
                </td>
                <td className="px-4 py-2">
                  <SeverityBadge severity={e.severity} />
                </td>
                <td className="px-4 py-2 font-mono text-xs text-ink-muted whitespace-nowrap">
                  {e.source_ip ?? "-"}
                </td>
                <td className="px-4 py-2 font-mono text-xs text-signal whitespace-nowrap">
                  {e.event_type}
                </td>
                <td className="px-4 py-2 font-mono text-xs text-ink-faint truncate max-w-md">
                  {e.raw_message}
                </td>
              </tr>
            ))}
            {results.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-10 text-center text-ink-faint text-sm">
                  {searched ? "No events matched your search." : "Run a search to see results."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
