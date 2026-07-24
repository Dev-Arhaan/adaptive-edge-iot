"use client";
import { useMemo } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import type { ClusterState, NodeState } from "@/lib/api";

function bucketLabel(battery: number): string {
  if (battery <= 20) return "0-20";
  if (battery <= 40) return "20-40";
  if (battery <= 60) return "40-60";
  if (battery <= 80) return "60-80";
  return "80-100";
}

export function BatteryDashboard({ nodes, clusters }: { nodes: NodeState[]; clusters: ClusterState[] }) {
  const distribution = useMemo(() => {
    const buckets: Record<string, number> = { "0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0 };
    nodes.forEach((n) => { buckets[bucketLabel(n.battery)] += 1; });
    return Object.entries(buckets).map(([bucket, count]) => ({ bucket, count }));
  }, [nodes]);

  const byCluster = useMemo(() => {
    const nodesById = new Map(nodes.map((n) => [n.id, n]));
    return clusters.map((c) => {
      const members = c.node_ids.map((id) => nodesById.get(id)).filter(Boolean) as NodeState[];
      const avg = members.length ? members.reduce((sum, n) => sum + n.battery, 0) / members.length : 0;
      return { cluster: c.id.replace("cluster-", "#"), average_battery: Number(avg.toFixed(1)) };
    });
  }, [nodes, clusters]);

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div className="rounded border border-panel-border bg-panel p-3">
        <h3 className="mb-2 font-display text-sm text-bone">Battery distribution</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={distribution}>
            <CartesianGrid stroke="#333B2C" strokeDasharray="3 3" />
            <XAxis dataKey="bucket" stroke="#8B9184" fontSize={11} />
            <YAxis stroke="#8B9184" fontSize={11} />
            <Tooltip contentStyle={{ background: "#1E2419", border: "1px solid #333B2C" }} />
            <Bar dataKey="count" fill="#8FBF6E" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="rounded border border-panel-border bg-panel p-3">
        <h3 className="mb-2 font-display text-sm text-bone">Average battery by cluster</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={byCluster}>
            <CartesianGrid stroke="#333B2C" strokeDasharray="3 3" />
            <XAxis dataKey="cluster" stroke="#8B9184" fontSize={11} />
            <YAxis stroke="#8B9184" fontSize={11} />
            <Tooltip contentStyle={{ background: "#1E2419", border: "1px solid #333B2C" }} />
            <Bar dataKey="average_battery" fill="#D9A441" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}