"use client";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ZAxis } from "recharts";
import type { SchedulingDecision } from "@/lib/api";

const RISK_ORDER: Record<string, number> = { low: 0, medium: 1, high: 2, emergency: 3 };
const RISK_COLORS: Record<string, string> = { low: "#6E9B7B", medium: "#D9A441", high: "#E4572E", emergency: "#C6362B" };

export function SchedulerTimeline({ decisions }: { decisions: SchedulingDecision[] }) {
  const data = decisions.map((d) => ({
    tick: d.tick, riskIndex: RISK_ORDER[d.risk_level], risk_level: d.risk_level, triggered_by: d.triggered_by, node_id: d.node_id,
  }));

  return (
    <div className="rounded border border-panel-border bg-panel p-3">
      <h3 className="mb-2 font-display text-sm text-bone">Scheduler timeline</h3>
      <ResponsiveContainer width="100%" height={220}>
        <ScatterChart>
          <CartesianGrid stroke="#333B2C" strokeDasharray="3 3" />
          <XAxis type="number" dataKey="tick" stroke="#8B9184" fontSize={11} name="tick" />
          <YAxis type="number" dataKey="riskIndex" stroke="#8B9184" fontSize={11} ticks={[0, 1, 2, 3]} tickFormatter={(v) => ["Low", "Medium", "High", "Emergency"][v]} />
          <ZAxis range={[40, 40]} />
          <Tooltip contentStyle={{ background: "#1E2419", border: "1px solid #333B2C" }} />
          <Scatter data={data}>
            {data.map((entry, index) => (
              <Cell key={index} fill={RISK_COLORS[entry.risk_level]} opacity={entry.triggered_by === "emergency_broadcast" ? 1 : 0.5} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
      <p className="mt-1 text-xs text-muted">Solid = emergency broadcast, faded = scheduled wake</p>
    </div>
  );
}