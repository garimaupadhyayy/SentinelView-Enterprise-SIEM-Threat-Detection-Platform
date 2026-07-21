import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { User } from "../types";
import { clearTokens, setTokens } from "../api/client";
import { fetchMe, login as apiLogin } from "../api/endpoints";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  hasRole: (...roles: User["role"][]) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("sv_access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    fetchMe()
      .then(setUser)
      .catch(() => clearTokens())
      .finally(() => setLoading(false));
  }, []);

  async function login(username: string, password: string) {
    const data = await apiLogin(username, password);
    setTokens(data.access_token, data.refresh_token);
    setUser(data.user);
  }

  function logout() {
    clearTokens();
    setUser(null);
  }

  function hasRole(...roles: User["role"][]) {
    return !!user && roles.includes(user.role);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
