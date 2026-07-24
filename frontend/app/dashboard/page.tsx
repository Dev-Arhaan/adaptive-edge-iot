"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ClusterState, MetricsSnapshot, NodeEvent, NodeState, SchedulingDecision, SimulationState } from "@/lib/api";
import { ForestMap } from "@/components/forest/ForestMap";
import { NodeCardGrid } from "@/components/nodes/NodeCardGrid";
import { ControlRail } from "@/components/layout/ControlRail";
import { LiveCharts } from "@/components/charts/LiveCharts";
import { BatteryDashboard } from "@/components/battery/BatteryDashboard";
import { RiskDashboard } from "@/components/risk/RiskDashboard";
import { SchedulerTimeline } from "@/components/scheduler/SchedulerTimeline";
import { EventLog } from "@/components/events/EventLog";

const POLL_INTERVAL_MS = 2000;
type ViewKind = "map" | "cards" | "charts" | "battery" | "risk" | "timeline";
const VIEWS: { key: ViewKind; label: string }[] = [
  { key: "map", label: "Map" }, { key: "cards", label: "Cards" }, { key: "charts", label: "Charts" },
  { key: "battery", label: "Battery" }, { key: "risk", label: "Risk" }, { key: "timeline", label: "Timeline" },
];

export default function DashboardPage() {
  const router = useRouter();
  const [state, setState] = useState<SimulationState | null>(null);
  const [nodes, setNodes] = useState<NodeState[]>([]);
  const [clusters, setClusters] = useState<ClusterState[]>([]);
  const [decisions, setDecisions] = useState<SchedulingDecision[]>([]);
  const [events, setEvents] = useState<NodeEvent[]>([]);
  const [metrics, setMetrics] = useState<MetricsSnapshot[]>([]);
  const [view, setView] = useState<ViewKind>("map");

  async function refresh() {
    try {
      const nextState = await api.getState();
      setState(nextState);
      if (nextState.started) {
        const [nextNodes, nextClusters, nextDecisions, nextEvents, nextMetrics] = await Promise.all([
          api.getNodes(), api.getClusters(), api.getSchedulingHistory(200), api.getEvents(100), api.getMetricsTimeSeries(),
        ]);
        setNodes(nextNodes); setClusters(nextClusters); setDecisions(nextDecisions); setEvents(nextEvents); setMetrics(nextMetrics);
      }
    } catch {
      router.push("/login");
    }
  }

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen">
      <ControlRail onStateChange={refresh} />

      <main className="flex flex-1 flex-col p-4">
        <header className="mb-4 flex items-center justify-between">
          <h1 className="font-display text-lg text-bone">Fire Watch — Live Console</h1>
          <div className="flex items-center gap-4 font-data text-xs text-muted">
            <span>Tick {state?.tick ?? "—"}</span>
            <span>{state?.node_count ?? 0} nodes</span>
            <span>{state?.cluster_count ?? 0} clusters</span>
            <span>Avg battery {state?.average_battery?.toFixed(0) ?? "—"}%</span>
          </div>
        </header>

        <div className="mb-3 flex w-fit overflow-hidden rounded border border-panel-border">
          {VIEWS.map((v) => (
            <button key={v.key} onClick={() => setView(v.key)} className={`px-3 py-1 text-sm ${view === v.key ? "bg-signal text-void" : "text-bone"}`}>
              {v.label}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-auto">
          {!state?.started ? (
            <div className="flex h-full items-center justify-center text-muted">Start a simulation from the left rail to bring the forest online.</div>
          ) : view === "map" ? (
            <ForestMap nodes={nodes} clusters={clusters} />
          ) : view === "cards" ? (
            <NodeCardGrid nodes={nodes} />
          ) : view === "charts" ? (
            <LiveCharts points={metrics} />
          ) : view === "battery" ? (
            <BatteryDashboard nodes={nodes} clusters={clusters} />
          ) : view === "risk" ? (
            <RiskDashboard nodes={nodes} />
          ) : (
            <SchedulerTimeline decisions={decisions} />
          )}
        </div>
      </main>

      <aside className="w-72 border-l border-panel-border p-4">
        <EventLog events={events} decisions={decisions} />
      </aside>
    </div>
  );
}