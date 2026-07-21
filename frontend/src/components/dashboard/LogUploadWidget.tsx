import { useRef, useState } from "react";
import { UploadCloud, CheckCircle2, XCircle } from "lucide-react";
import { uploadLogFile } from "../../api/endpoints";
import type { SourceType } from "../../types";

const SOURCE_OPTIONS: { value: SourceType; label: string }[] = [
  { value: "ssh_auth", label: "SSH Auth Log" },
  { value: "web_access", label: "Web Access Log" },
  { value: "firewall", label: "Firewall / iptables Log" },
];

export function LogUploadWidget({ onUploaded }: { onUploaded?: () => void }) {
  const [sourceType, setSourceType] = useState<SourceType>("ssh_auth");
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setStatus("uploading");
    try {
      const events = await uploadLogFile(sourceType, file);
      setStatus("success");
      setMessage(`Ingested ${events.length} events from ${file.name}`);
      onUploaded?.();
    } catch (err: any) {
      setStatus("error");
      setMessage(err?.response?.data?.detail || "Upload failed — check the file matches the selected format.");
    } finally {
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  return (
    <div className="panel p-4">
      <h3 className="font-display font-semibold text-sm mb-3">Ingest Log File</h3>
      <div className="flex items-center gap-2 mb-3">
        <select
          value={sourceType}
          onChange={(e) => setSourceType(e.target.value as SourceType)}
          className="bg-base-800 border border-line rounded-md px-2.5 py-1.5 text-xs font-mono flex-1 focus:outline-none focus:ring-2 focus:ring-signal/40"
        >
          {SOURCE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>

      <label className="flex flex-col items-center justify-center gap-2 border-2 border-dashed border-line rounded-md py-6 cursor-pointer hover:border-signal/40 hover:bg-signal/5 transition-colors">
        <UploadCloud className="h-5 w-5 text-ink-faint" />
        <span className="text-xs text-ink-muted">
          {status === "uploading" ? "Uploading…" : "Click to select a log file"}
        </span>
        <input
          ref={fileRef}
          type="file"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
      </label>

      {status === "success" && (
        <div className="mt-3 flex items-center gap-2 text-xs text-signal">
          <CheckCircle2 className="h-4 w-4" /> {message}
        </div>
      )}
      {status === "error" && (
        <div className="mt-3 flex items-center gap-2 text-xs text-sev-critical">
          <XCircle className="h-4 w-4" /> {message}
        </div>
      )}
    </div>
  );
}
