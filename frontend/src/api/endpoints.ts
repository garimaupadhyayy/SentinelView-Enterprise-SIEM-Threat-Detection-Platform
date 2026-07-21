import { api } from "./client";
import type {
  Alert,
  AlertStatus,
  DashboardSummary,
  DetectionRule,
  EventRecord,
  GeoPoint,
  MitreTechnique,
  Severity,
  TimeseriesBucket,
  User,
} from "../types";

// --- Auth ---
export async function login(username: string, password: string) {
  const res = await api.post("/auth/login", { username, password });
  return res.data as { access_token: string; refresh_token: string; user: User };
}

export async function register(username: string, email: string, password: string) {
  const res = await api.post("/auth/register", { username, email, password });
  return res.data as User;
}

export async function fetchMe() {
  const res = await api.get("/auth/me");
  return res.data as User;
}

// --- Dashboard ---
export async function fetchSummary(minutes = 60) {
  const res = await api.get("/dashboard/summary", { params: { minutes } });
  return res.data as DashboardSummary;
}

export async function fetchGeomap(minutes = 60) {
  const res = await api.get("/dashboard/geomap", { params: { minutes } });
  return res.data as { points: GeoPoint[] };
}

export async function fetchMitreHeatmap(days = 7) {
  const res = await api.get("/dashboard/mitre-heatmap", { params: { days } });
  return res.data as { techniques: MitreTechnique[] };
}

export async function fetchTimeseries(hours = 24, bucket_minutes = 30) {
  const res = await api.get("/dashboard/events-timeseries", { params: { hours, bucket_minutes } });
  return res.data as { bucket_minutes: number; buckets: TimeseriesBucket[] };
}

// --- Alerts ---
export async function fetchAlerts(params: {
  severity?: Severity;
  status?: AlertStatus;
  source_ip?: string;
  limit?: number;
  offset?: number;
  sort_by?: string;
  order?: string;
}) {
  const res = await api.get("/alerts", { params });
  return res.data as Alert[];
}

export async function fetchAlert(id: number) {
  const res = await api.get(`/alerts/${id}`);
  return res.data as Alert;
}

export async function fetchAlertEvents(id: number) {
  const res = await api.get(`/alerts/${id}/events`);
  return res.data as EventRecord[];
}

export async function updateAlertStatus(id: number, status: AlertStatus) {
  const res = await api.patch(`/alerts/${id}/status`, { status });
  return res.data as Alert;
}

// --- Events / log search ---
export async function searchEvents(params: {
  q?: string;
  source_ip?: string;
  severity?: Severity;
  source_type?: string;
  event_type?: string;
  user?: string;
  limit?: number;
  offset?: number;
}) {
  const res = await api.get("/events/search", { params });
  return res.data as EventRecord[];
}

export async function uploadLogFile(sourceType: string, file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/events/upload", form, {
    params: { source_type: sourceType },
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data as EventRecord[];
}

// --- Rules ---
export async function fetchRules() {
  const res = await api.get("/rules");
  return res.data as DetectionRule[];
}

export async function fetchRuleTypes() {
  const res = await api.get("/rules/types");
  return res.data as string[];
}

export async function createRule(payload: Partial<DetectionRule>) {
  const res = await api.post("/rules", payload);
  return res.data as DetectionRule;
}

export async function updateRule(id: number, payload: Partial<DetectionRule>) {
  const res = await api.patch(`/rules/${id}`, payload);
  return res.data as DetectionRule;
}

export async function deleteRule(id: number) {
  await api.delete(`/rules/${id}`);
}

// --- Reports ---
async function downloadReport(path: string, params: Record<string, string | number>, fallbackName: string) {
  const res = await api.get(path, { params, responseType: "blob" });
  const disposition: string | undefined = res.headers["content-disposition"];
  let filename = fallbackName;
  const match = disposition?.match(/filename=([^;]+)/);
  if (match) filename = match[1].trim();

  const url = window.URL.createObjectURL(new Blob([res.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export function downloadCsvReport(params: { alert_id?: number; start?: string; end?: string }) {
  return downloadReport("/reports/incident.csv", params as Record<string, string | number>, "incident_report.csv");
}

export function downloadPdfReport(params: { alert_id?: number; start?: string; end?: string }) {
  return downloadReport("/reports/incident.pdf", params as Record<string, string | number>, "incident_report.pdf");
}
