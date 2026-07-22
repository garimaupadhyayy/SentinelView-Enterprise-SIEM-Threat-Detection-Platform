import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Radar, ArrowRight, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      navigate("/");
    } catch {
      setError("Invalid username or password.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden">
      <div className="absolute inset-0 bg-scan pointer-events-none" />
      <div className="w-full max-w-sm relative">
        <div className="flex items-center gap-2.5 justify-center mb-8">
          <Radar className="h-8 w-8 text-signal" strokeWidth={2.2} />
          <span className="font-display font-semibold text-2xl tracking-tight">
            Sentinel<span className="text-signal">View</span>
          </span>
        </div>

        <form onSubmit={handleSubmit} className="panel p-6 space-y-4">
          <div>
            <h1 className="font-display font-semibold text-lg">Analyst sign-in</h1>
            <p className="text-sm text-ink-muted mt-1">Access the correlation console.</p>
          </div>

          {error && (
            <div className="flex items-center gap-2 text-sm text-sev-critical bg-sev-critical/10 border border-sev-critical/30 rounded-md px-3 py-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {error}
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase tracking-wide text-ink-faint">
              Username
            </label>
            <input
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-base-800 border border-line rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/40 focus:border-signal/50"
              placeholder="admin"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono uppercase tracking-wide text-ink-faint">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-base-800 border border-line rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/40 focus:border-signal/50"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full flex items-center justify-center gap-2 bg-signal text-base-950 font-medium rounded-md py-2.5 text-sm hover:bg-signal-glow transition-colors disabled:opacity-50"
          >
            {submitting ? "Signing in…" : "Sign in"}
            {!submitting && <ArrowRight className="h-4 w-4" />}
          </button>

          <p className="text-xs text-ink-faint text-center pt-2">
            Demo credentials (after seeding): admin / analyst / viewer — password{" "}
            <span className="font-mono">ChangeMe123!</span>
          </p>
        </form>
      </div>
    </div>
  );
}
