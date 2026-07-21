import { useState } from "react";
import type { GeoPoint } from "../../types";

/**
 * Lightweight geo-distribution widget: plots source IPs on an
 * equirectangular (lon/lat -> x/y) projection using inline SVG continent
 * outlines, sized/colored by hit count. No external map tiles or API key
 * required (beyond the free ip-api.com geolocation lookup already used
 * server-side), which keeps the single-node/self-hosted deployment story
 * intact.
 */
function project(lon: number, lat: number, width: number, height: number) {
  const x = ((lon + 180) / 360) * width;
  const y = ((90 - lat) / 180) * height;
  return { x, y };
}

// Very simplified continent silhouettes (low-fidelity, intentionally --
// this is a threat-distribution indicator, not a navigational map).
const LANDMASSES = [
  "M 90 70 L 170 60 L 230 90 L 250 140 L 210 180 L 150 190 L 100 160 L 80 110 Z", // N. America
  "M 180 210 L 220 200 L 250 260 L 230 330 L 190 340 L 165 270 Z", // S. America
  "M 380 70 L 460 60 L 500 100 L 480 140 L 420 130 L 390 100 Z", // Europe
  "M 400 150 L 470 145 L 500 220 L 470 300 L 420 310 L 395 220 Z", // Africa
  "M 500 70 L 640 60 L 700 120 L 660 180 L 560 190 L 500 140 Z", // Asia
  "M 620 260 L 680 255 L 700 290 L 660 305 L 615 285 Z", // Oceania
];

export function GeoMap({ points }: { points: GeoPoint[] }) {
  const [hovered, setHovered] = useState<GeoPoint | null>(null);
  const width = 760;
  const height = 360;
  const maxCount = Math.max(1, ...points.map((p) => p.count));

  return (
    <div className="panel p-4 relative">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-display font-semibold text-sm">Source IP Geo Distribution</h3>
        <span className="text-xs font-mono text-ink-faint">{points.length} locations</span>
      </div>

      <div className="rounded-md overflow-hidden border border-line bg-base-950">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
          <rect width={width} height={height} fill="#080B0F" />
          {LANDMASSES.map((d, i) => (
            <path key={i} d={d} fill="#121A22" stroke="#1A2530" strokeWidth={1} />
          ))}
          {points.map((p) => {
            const { x, y } = project(p.lon, p.lat, width, height);
            const r = 3 + (p.count / maxCount) * 9;
            return (
              <g key={p.source_ip}>
                <circle
                  cx={x}
                  cy={y}
                  r={r}
                  fill="#EF5A5A"
                  fillOpacity={0.25}
                  stroke="#EF5A5A"
                  strokeWidth={1}
                  className="cursor-pointer"
                  onMouseEnter={() => setHovered(p)}
                  onMouseLeave={() => setHovered(null)}
                />
                <circle cx={x} cy={y} r={2} fill="#EF5A5A" />
              </g>
            );
          })}
        </svg>
      </div>

      {hovered && (
        <div className="absolute bottom-6 left-6 panel px-3 py-2 text-xs font-mono shadow-glow">
          <div className="text-ink font-semibold">{hovered.source_ip}</div>
          <div className="text-ink-muted">
            {hovered.city}, {hovered.country}
          </div>
          <div className="text-signal">{hovered.count} events</div>
        </div>
      )}

      {points.length === 0 && (
        <p className="text-sm text-ink-faint text-center py-4">
          No geolocated source IPs in this window yet.
        </p>
      )}
    </div>
  );
}
