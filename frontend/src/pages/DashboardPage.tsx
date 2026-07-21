import { useEffect, useState, useCallback } from "react";
import { Activity, ShieldAlert, Gauge, Zap } from "lucide-react";
import {
  fetchSummary,
  fetchGeomap,
  fetchMitreHeatmap,
  fetchTimeseries,
} from "../api/endpoints";
import type { DashboardSummary, GeoPoint, MitreTechnique, TimeseriesBucket } from "../types";
import { StatCard } from "../components/dashboard/StatCard";
import { EventsTimeseriesChart } from "../components/dashboard/EventsTimeseriesChart";
import { SeverityBreakdownChart } from "../components/dashboard/SeverityBreakdownChart";
import { MitreHeatmap } from "../components/dashboard/MitreHeatmap";
import { GeoMap } from "../components/dashboard/GeoMap";
import { TopSourceIps } from "../components/dashboard/TopSourceIps";
import { LiveEventTail } from "../components/dashboard/LiveEventTail";
import { LogUploadWidget } from "../components/dashboard/LogUploadWidget";

const REFRESH_MS = 15000;

export function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [buckets, setBuckets] = useState<TimeseriesBucket[]>([]);
  const [geoPoints, setGeoPoints] = useState<GeoPoint[]>([]);
  const [techniques, setTechniques] = useState<MitreTechnique[]>([]);

  const loadAll = useCallback(async () => {
    const [s, ts, geo, mitre] = await Promise.all([
      fetchSummary(60),
      fetchTimeseries(24, 30),
      fetchGeomap(120),
      fetchMitreHeatmap(7),
    ]);
    setSummary(s);
    setBuckets(ts.buckets);
    setGeoPoints(geo.points);
    setTechniques(mitre.techniques);
  }, []);

  useEffect(() => {
    loadAll();
    const interval = setInterval(loadAll, REFRESH_MS);
    return () => clearInterval(interval);
  }, [loadAll]);

  return (
    <div className="p-6 space-y-6 max-w-[1600px]">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold">Operations Overview</h1>
          <p className="text-sm text-ink-muted mt-1">
            Real-time correlation status across all ingested log sources.
          </p>
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            label="Events / sec"
            value={summary.events_per_second.toFixed(2)}
            sub={`${summary.total_events_in_window} in last ${summary.window_minutes}m`}
            icon={<Activity className="h-4 w-4" />}
          />
          <StatCard
            label="New Alerts"
            value={summary.new_alerts}
            sub={`${summary.total_alerts} total`}
            icon={<ShieldAlert className="h-4 w-4" />}
            accent={summary.new_alerts > 0 ? "critical" : "default"}
          />
          <StatCard
            label="Critical Alerts"
            value={summary.alert_counts_by_severity.critical ?? 0}
            sub="requires immediate triage"
            icon={<Zap className="h-4 w-4" />}
            accent="critical"
          />
          <StatCard
            label="Total Events"
            value={summary.total_events.toLocaleString()}
            sub="all time"
            icon={<Gauge className="h-4 w-4" />}
            accent="signal"
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <EventsTimeseriesChart buckets={buckets} />
          <GeoMap points={geoPoints} />
        </div>
        <div className="space-y-4">
          <LogUploadWidget onUploaded={loadAll} />
          {summary && <TopSourceIps summary={summary} />}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {summary && (
          <div className="lg:col-span-1">
            <SeverityBreakdownChart summary={summary} />
          </div>
        )}
        <div className="lg:col-span-1">
          <MitreHeatmap techniques={techniques} />
        </div>
        <div className="lg:col-span-1">
          <LiveEventTail />
        </div>
      </div>
    </div>
  );
}
