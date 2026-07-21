import { useEffect, useState, type FormEvent } from "react";
import { Plus, Trash2, X } from "lucide-react";
import { createRule, deleteRule, fetchRuleTypes, fetchRules, updateRule } from "../api/endpoints";
import type { DetectionRule } from "../types";
import { useAuth } from "../context/AuthContext";

const RULE_TYPE_LABELS: Record<string, string> = {
  brute_force: "Brute Force",
  port_scan: "Port Scan",
  impossible_travel: "Impossible Travel",
  priv_escalation: "Privilege Escalation",
  web_attack_signature: "Web Attack Signature",
  threshold_generic: "Generic Threshold",
};

function ConfigPreview({ config }: { config: Record<string, unknown> }) {
  const entries = Object.entries(config ?? {});
  if (entries.length === 0) return <span className="text-ink-faint">—</span>;
  return (
    <div className="flex flex-wrap gap-1">
      {entries.map(([k, v]) => (
        <span
          key={k}
          className="font-mono text-[10px] bg-base-800 border border-line rounded px-1.5 py-0.5 text-ink-muted"
        >
          {k}={String(v)}
        </span>
      ))}
    </div>
  );
}

function NewRuleForm({
  ruleTypes,
  onCreated,
  onClose,
}: {
  ruleTypes: string[];
  onCreated: (r: DetectionRule) => void;
  onClose: () => void;
}) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [ruleType, setRuleType] = useState(ruleTypes[0] ?? "threshold_generic");
  const [severity, setSeverity] = useState("medium");
  const [weight, setWeight] = useState(1);
  const [windowSeconds, setWindowSeconds] = useState(300);
  const [threshold, setThreshold] = useState(5);
  const [mitreId, setMitreId] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const rule = await createRule({
        name,
        description,
        rule_type: ruleType,
        severity,
        weight,
        mitre_technique_id: mitreId || undefined,
        config: { window_seconds: windowSeconds, threshold },
      });
      onCreated(rule);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Failed to create rule.");
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <form
        onSubmit={handleSubmit}
        onClick={(e) => e.stopPropagation()}
        className="panel p-6 w-full max-w-md space-y-4"
      >
        <div className="flex items-center justify-between">
          <h2 className="font-display font-semibold text-lg">New Custom Rule</h2>
          <button type="button" onClick={onClose} className="text-ink-faint hover:text-ink">
            <X className="h-5 w-5" />
          </button>
        </div>

        {error && (
          <div className="text-sm text-sev-critical bg-sev-critical/10 border border-sev-critical/30 rounded-md px-3 py-2">
            {error}
          </div>
        )}

        <div className="space-y-1.5">
          <label className="text-xs font-mono uppercase text-ink-faint">Name</label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-base-800 border border-line rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/40"
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-mono uppercase text-ink-faint">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
            className="w-full bg-base-800 border border-line rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/40"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase text-ink-faint">Rule Type</label>
            <select
              value={ruleType}
              onChange={(e) => setRuleType(e.target.value)}
              className="w-full bg-base-800 border border-line rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/40"
            >
              {ruleTypes.map((t) => (
                <option key={t} value={t}>
                  {RULE_TYPE_LABELS[t] ?? t}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase text-ink-faint">Severity</label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="w-full bg-base-800 border border-line rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/40"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase text-ink-faint">Window (s)</label>
            <input
              type="number"
              value={windowSeconds}
              onChange={(e) => setWindowSeconds(Number(e.target.value))}
              className="w-full bg-base-800 border border-line rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/40"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase text-ink-faint">Threshold</label>
            <input
              type="number"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-full bg-base-800 border border-line rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/40"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase text-ink-faint">Weight</label>
            <input
              type="number"
              value={weight}
              onChange={(e) => setWeight(Number(e.target.value))}
              className="w-full bg-base-800 border border-line rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/40"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-mono uppercase text-ink-faint">
            MITRE Technique ID (optional)
          </label>
          <input
            value={mitreId}
            onChange={(e) => setMitreId(e.target.value)}
            placeholder="e.g. T1110"
            className="w-full bg-base-800 border border-line rounded-md px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-signal/40"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-signal text-base-950 font-medium rounded-md py-2.5 text-sm hover:bg-signal-glow transition-colors"
        >
          Create Rule
        </button>
      </form>
    </div>
  );
}

export function RulesPage() {
  const { hasRole } = useAuth();
  const isAdmin = hasRole("admin");
  const [rules, setRules] = useState<DetectionRule[]>([]);
  const [ruleTypes, setRuleTypes] = useState<string[]>([]);
  const [showForm, setShowForm] = useState(false);

  async function load() {
    const [r, t] = await Promise.all([fetchRules(), fetchRuleTypes()]);
    setRules(r);
    setRuleTypes(t);
  }

  useEffect(() => {
    load();
  }, []);

  async function toggleEnabled(rule: DetectionRule) {
    const updated = await updateRule(rule.id, { enabled: !rule.enabled });
    setRules((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
  }

  async function handleDelete(rule: DetectionRule) {
    if (!confirm(`Delete rule "${rule.name}"?`)) return;
    await deleteRule(rule.id);
    setRules((prev) => prev.filter((r) => r.id !== rule.id));
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Detection Rules</h1>
          <p className="text-sm text-ink-muted mt-1">
            Every alert traces back to one of these rules. New rule = new config entry, not a
            code change.
          </p>
        </div>
        {isAdmin && (
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-1.5 bg-signal text-base-950 font-medium rounded-md px-4 py-2 text-sm hover:bg-signal-glow transition-colors"
          >
            <Plus className="h-4 w-4" /> New Rule
          </button>
        )}
      </div>

      <div className="panel overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-base-800/60 text-xs font-mono uppercase text-ink-faint">
            <tr>
              <th className="text-left px-4 py-2.5 font-medium">Name</th>
              <th className="text-left px-4 py-2.5 font-medium">Type</th>
              <th className="text-left px-4 py-2.5 font-medium">MITRE</th>
              <th className="text-left px-4 py-2.5 font-medium">Config</th>
              <th className="text-left px-4 py-2.5 font-medium">Severity</th>
              <th className="text-left px-4 py-2.5 font-medium">Enabled</th>
              {isAdmin && <th className="text-left px-4 py-2.5 font-medium">Actions</th>}
            </tr>
          </thead>
          <tbody>
            {rules.map((r) => (
              <tr key={r.id} className="border-t border-line hover:bg-base-800/40">
                <td className="px-4 py-2.5">
                  <div className="font-medium">{r.name}</div>
                  {r.is_builtin && (
                    <span className="text-[10px] font-mono text-signal">built-in</span>
                  )}
                </td>
                <td className="px-4 py-2.5 font-mono text-xs text-ink-muted">
                  {RULE_TYPE_LABELS[r.rule_type] ?? r.rule_type}
                </td>
                <td className="px-4 py-2.5 font-mono text-xs text-ink-muted">
                  {r.mitre_technique_id ?? "-"}
                </td>
                <td className="px-4 py-2.5">
                  <ConfigPreview config={r.config} />
                </td>
                <td className="px-4 py-2.5 font-mono text-xs uppercase text-ink-muted">
                  {r.severity}
                </td>
                <td className="px-4 py-2.5">
                  <button
                    disabled={!isAdmin}
                    onClick={() => toggleEnabled(r)}
                    className={`relative w-9 h-5 rounded-full transition-colors ${
                      r.enabled ? "bg-signal" : "bg-base-700"
                    } ${!isAdmin ? "opacity-50 cursor-not-allowed" : ""}`}
                  >
                    <span
                      className={`absolute top-0.5 h-4 w-4 rounded-full bg-base-950 transition-transform ${
                        r.enabled ? "translate-x-4" : "translate-x-0.5"
                      }`}
                    />
                  </button>
                </td>
                {isAdmin && (
                  <td className="px-4 py-2.5">
                    {!r.is_builtin && (
                      <button
                        onClick={() => handleDelete(r)}
                        className="text-ink-faint hover:text-sev-critical"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <NewRuleForm
          ruleTypes={ruleTypes}
          onClose={() => setShowForm(false)}
          onCreated={(r) => {
            setRules((prev) => [...prev, r]);
            setShowForm(false);
          }}
        />
      )}
    </div>
  );
}
