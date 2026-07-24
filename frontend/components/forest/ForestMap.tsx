"use client";

import { useMemo } from "react";
import ReactFlow, { Background, Node as FlowNode, Edge } from "reactflow";
import "reactflow/dist/style.css";
import type { ClusterState, NodeState } from "@/lib/api";

const RISK_COLORS: Record<string, string> = {
  low: "#6E9B7B", medium: "#D9A441", high: "#E4572E", emergency: "#C6362B",
};

function riskColor(level: string | null): string {
  return level ? RISK_COLORS[level] ?? "#8B9184" : "#8B9184"; // muted gray = no reading yet
}

export function ForestMap({ nodes, clusters }: { nodes: NodeState[]; clusters: ClusterState[] }) {
  const flowNodes: FlowNode[] = useMemo(
    () =>
      nodes.map((n) => ({
        id: n.id,
        position: { x: n.x, y: n.y },
        data: { label: "" },
        style: {
          width: n.health === "dead" ? 6 : n.sleep_state === "awake" ? 14 : 9,
          height: n.health === "dead" ? 6 : n.sleep_state === "awake" ? 14 : 9,
          borderRadius: "50%",
          background: n.health === "dead" ? "#4A4E44" : riskColor(n.last_risk_level),
          border: n.sleep_state === "awake" ? "2px solid #E8E6DE" : "1px solid transparent",
          boxShadow: n.sleep_state === "awake" ? `0 0 12px ${riskColor(n.last_risk_level)}` : "none",
          transition: "all 400ms ease",
        },
      })),
    [nodes]
  );

  // Cluster boundary as centroid + radius, not a convex hull — a convex
  // hull would be more precise, but a circle is honest enough at this
  // density and far simpler to keep correct.
  const clusterNodes: FlowNode[] = useMemo(
    () =>
      clusters.map((c) => {
        const radius = 40 + c.node_ids.length * 6;
        return {
          id: `cluster-${c.id}`,
          position: { x: c.center_x - radius, y: c.center_y - radius },
          data: { label: "" },
          style: {
            width: radius * 2, height: radius * 2, borderRadius: "50%",
            background: "rgba(143, 191, 110, 0.05)", border: "1px dashed rgba(143, 191, 110, 0.25)",
          },
          draggable: false, selectable: false,
        };
      }),
    [clusters]
  );

  return (
    <div className="h-full w-full rounded-lg border border-panel-border bg-panel">
      <ReactFlow nodes={[...clusterNodes, ...flowNodes]} edges={[] as Edge[]} fitView proOptions={{ hideAttribution: true }}>
        <Background color="#333B2C" gap={32} />
      </ReactFlow>
    </div>
  );
}