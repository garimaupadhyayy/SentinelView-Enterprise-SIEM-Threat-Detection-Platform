import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  ShieldAlert,
  Search,
  Settings2,
  Radar,
  LogOut,
  Wifi,
  WifiOff,
} from "lucide-react";
import clsx from "clsx";
import { useAuth } from "../../context/AuthContext";
import { useLiveStream } from "../../hooks/useLiveStream";
import type { EventRecord } from "../../types";

const NAV_ITEMS = [
  { to: "/", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/alerts", label: "Alert Triage", icon: ShieldAlert },
  { to: "/search", label: "Log Search", icon: Search },
  { to: "/rules", label: "Detection Rules", icon: Settings2 },
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const { connected } = useLiveStream<EventRecord>("/ws/events", 1);

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 shrink-0 border-r border-line bg-base-900/60 backdrop-blur flex flex-col">
        <div className="px-5 py-5 border-b border-line">
          <div className="flex items-center gap-2">
            <Radar className="h-6 w-6 text-signal" strokeWidth={2.2} />
            <span className="font-display font-semibold text-lg tracking-tight">
              Sentinel<span className="text-signal">View</span>
            </span>
          </div>
          <div className="mt-3 flex items-center gap-1.5 text-xs font-mono text-ink-faint">
            {connected ? (
              <>
                <Wifi className="h-3 w-3 text-signal" />
                <span className="text-signal">live</span>
              </>
            ) : (
              <>
                <WifiOff className="h-3 w-3" />
                <span>reconnecting…</span>
              </>
            )}
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  isActive
                    ? "bg-signal/10 text-signal border border-signal/20"
                    : "text-ink-muted hover:text-ink hover:bg-base-800 border border-transparent"
                )
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-3 py-4 border-t border-line">
          <div className="px-3 py-2 mb-2">
            <div className="text-sm font-medium">{user?.username}</div>
            <div className="text-xs font-mono text-ink-faint uppercase">{user?.role}</div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-ink-muted hover:text-sev-critical hover:bg-sev-critical/10 transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        <Outlet />
      </main>
    </div>
  );
}
