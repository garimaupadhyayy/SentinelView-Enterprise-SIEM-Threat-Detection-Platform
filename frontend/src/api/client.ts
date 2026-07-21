import axios from "axios";

export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
export const WS_BASE = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export const api = axios.create({ baseURL: API_BASE });

function getTokens() {
  return {
    access: localStorage.getItem("sv_access_token"),
    refresh: localStorage.getItem("sv_refresh_token"),
  };
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem("sv_access_token", access);
  localStorage.setItem("sv_refresh_token", refresh);
}

export function clearTokens() {
  localStorage.removeItem("sv_access_token");
  localStorage.removeItem("sv_refresh_token");
}

api.interceptors.request.use((config) => {
  const { access } = getTokens();
  if (access) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const { refresh } = getTokens();
  if (!refresh) return null;
  try {
    const resp = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refresh });
    setTokens(resp.data.access_token, resp.data.refresh_token);
    return resp.data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      if (!refreshPromise) refreshPromise = refreshAccessToken();
      const newToken = await refreshPromise;
      refreshPromise = null;
      if (newToken) {
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      }
      clearTokens();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
