import clsx from "clsx";
import type { MitreTechnique } from "../../types";

function intensityClass(count: number, max: number) {
  const ratio = max > 0 ? count / max : 0;
  if (ratio === 0) return "bg-base-800 text-ink-faint border-line";
  if (ratio < 0.25) return "bg-sev-info/10 text-sev-info border-sev-info/30";
  if (ratio < 0.5) return "bg-sev-medium/10 text-sev-medium border-sev-medium/30";
  if (ratio < 0.75) return "bg-sev-high/15 text-sev-high border-sev-high/40";
  return "bg-sev-critical/20 text-sev-critical border-sev-critical/50";
}

export function MitreHeatmap({ techniques }: { techniques: MitreTechnique[] }) {
  const max = Math.max(0, ...techniques.map((t) => t.count));

  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display font-semibold text-sm">MITRE ATT&amp;CK Coverage</h3>
        <span className="text-xs font-mono text-ink-faint">last 7d</span>
      </div>
      {techniques.length === 0 ? (
        <p className="text-sm text-ink-faint py-6 text-center">No technique data yet.</p>
      ) : (
        <div className="grid grid-cols-2 gap-2">
          {techniques
            .sort((a, b) => b.count - a.count)
            .map((t) => (
              <div
                key={t.technique_id}
                className={clsx(
                  "rounded-md border px-3 py-2 flex items-center justify-between",
                  intensityClass(t.count, max)
                )}
              >
                <div className="min-w-0">
                  <div className="font-mono text-xs font-semibold">{t.technique_id}</div>
                  <div className="text-xs truncate opacity-80">{t.technique_name}</div>
                </div>
                <div className="font-display font-bold text-lg pl-2">{t.count}</div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
