"use client";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { MetricsSnapshot } from "@/lib/api";

export function LiveCharts({ points }: { points: MetricsSnapshot[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div className="rounded border border-panel-border bg-panel p-3">
        <h3 className="mb-2 font-display text-sm text-bone">Average sensing interval</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={points}>
            <CartesianGrid stroke="#333B2C" strokeDasharray="3 3" />
            <XAxis dataKey="tick" stroke="#8B9184" fontSize={11} />
            <YAxis stroke="#8B9184" fontSize={11} />
            <Tooltip contentStyle={{ background: "#1E2419", border: "1px solid #333B2C" }} />
            <Line type="monotone" dataKey="average_interval_seconds" stroke="#8FBF6E" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="rounded border border-panel-border bg-panel p-3">
        <h3 className="mb-2 font-display text-sm text-bone">Emergency wakes per interval</h3>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={points}>
            <CartesianGrid stroke="#333B2C" strokeDasharray="3 3" />
            <XAxis dataKey="tick" stroke="#8B9184" fontSize={11} />
            <YAxis stroke="#8B9184" fontSize={11} />
            <Tooltip contentStyle={{ background: "#1E2419", border: "1px solid #333B2C" }} />
            <Line type="monotone" dataKey="emergency_wakes_since_last" stroke="#E4572E" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}