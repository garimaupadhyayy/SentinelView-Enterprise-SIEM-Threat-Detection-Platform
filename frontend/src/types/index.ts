export type Severity = "info" | "low" | "medium" | "high" | "critical";
export type SourceType = "ssh_auth" | "web_access" | "firewall" | "windows_event" | "generic";
export type AlertStatus = "new" | "investigating" | "resolved" | "false_positive";
export type UserRole = "admin" | "analyst" | "viewer";

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export interface EventRecord {
  id: number;
  timestamp: string;
  source_ip: string | null;
  destination_ip: string | null;
  event_type: string;
  severity: Severity;
  raw_message: string;
  source_type: SourceType;
  user: string | null;
  status_code: string | null;
  port: number | null;
  url_path: string | null;
  ingested_at: string;
}

export interface Alert {
  id: number;
  rule_id: number | null;
  rule_name: string;
  mitre_technique_id: string | null;
  mitre_technique_name: string | null;
  severity: Severity;
  status: AlertStatus;
  source_ip: string | null;
  target: string | null;
  title: string;
  description: string;
  event_count: number;
  first_seen: string;
  last_seen: string;
  created_at: string;
  updated_at: string;
}

export interface DetectionRule {
  id: number;
  name: string;
  description: string | null;
  rule_type: string;
  mitre_technique_id: string | null;
  mitre_technique_name: string | null;
  severity: string;
  weight: number;
  config: Record<string, unknown>;
  enabled: boolean;
  is_builtin: boolean;
  created_at: string;
  updated_at: string;
}

export interface DashboardSummary {
  generated_at: string;
  window_minutes: number;
  total_events: number;
  total_events_in_window: number;
  events_per_second: number;
  total_alerts: number;
  new_alerts: number;
  alert_counts_by_severity: Partial<Record<Severity, number>>;
  alert_counts_by_status: Partial<Record<AlertStatus, number>>;
  top_source_ips: { source_ip: string; count: number }[];
}

export interface GeoPoint {
  source_ip: string;
  count: number;
  lat: number;
  lon: number;
  city: string;
  country: string;
}

export interface MitreTechnique {
  technique_id: string;
  technique_name: string;
  count: number;
}

export interface TimeseriesBucket {
  timestamp: string;
  count: number;
}
