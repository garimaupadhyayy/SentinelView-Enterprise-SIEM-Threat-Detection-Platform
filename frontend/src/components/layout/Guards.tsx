import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import type { UserRole } from "../../types";

export function RequireAuth() {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-ink-faint font-mono text-sm">
        Authenticating…
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function RequireRole({ roles }: { roles: UserRole[] }) {
  const { user } = useAuth();
  if (!user || !roles.includes(user.role)) {
    return (
      <div className="p-10">
        <div className="panel p-6 max-w-md">
          <h2 className="font-display font-semibold text-lg text-sev-high">Access restricted</h2>
          <p className="mt-2 text-sm text-ink-muted">
            Your role (<span className="font-mono text-ink">{user?.role}</span>) doesn't have
            permission to view this page. Contact an admin if you need access.
          </p>
        </div>
      </div>
    );
  }
  return <Outlet />;
}
