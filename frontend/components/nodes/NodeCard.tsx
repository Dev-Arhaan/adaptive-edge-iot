import type { NodeState } from "@/lib/api";

const RISK_LABEL: Record<string, string> = { low: "Low", medium: "Medium", high: "High", emergency: "Emergency" };
const RISK_BG: Record<string, string> = {
  low: "rgba(110,155,123,0.2)", medium: "rgba(217,164,65,0.2)",
  high: "rgba(228,87,46,0.2)", emergency: "rgba(198,54,43,0.25)",
};

export function NodeCard({ node }: { node: NodeState }) {
  const risk = node.last_risk_level;
  return (
    <div className="rounded border border-panel-border bg-panel p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="font-data text-xs text-muted">{node.id}</span>
        <span className="rounded px-2 py-0.5 font-display text-xs" style={{ background: risk ? RISK_BG[risk] : "transparent" }}>
          {node.health === "dead" ? "Offline" : risk ? RISK_LABEL[risk] : "—"}
        </span>
      </div>
      <dl className="grid grid-cols-2 gap-x-3 gap-y-1 font-data text-xs text-bone">
        <dt className="text-muted">Temp</dt><dd>{node.temperature.toFixed(1)}°C</dd>
        <dt className="text-muted">Humidity</dt><dd>{node.humidity.toFixed(0)}%</dd>
        <dt className="text-muted">Smoke</dt><dd>{node.smoke.toFixed(2)}</dd>
        <dt className="text-muted">Battery</dt><dd>{node.battery.toFixed(0)}%</dd>
        <dt className="text-muted">Interval</dt><dd>{node.sensing_interval_seconds}s</dd>
        <dt className="text-muted">State</dt><dd>{node.sleep_state}</dd>
      </dl>
    </div>
  );
}