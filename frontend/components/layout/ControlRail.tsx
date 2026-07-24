"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export function ControlRail({ onStateChange }: { onStateChange: () => void }) {
  const [schedulerKind, setSchedulerKind] = useState("adaptive_rule_based");
  const [nodeCount, setNodeCount] = useState(150);

  async function handleStart() {
    await api.startSimulation(nodeCount, schedulerKind);
    onStateChange();
  }

  return (
    <aside className="flex w-56 flex-col gap-4 border-r border-panel-border bg-panel p-4">
      <div>
        <h2 className="mb-2 font-display text-sm tracking-wide text-bone">Session</h2>
        <label className="mb-1 block text-xs text-muted">Nodes</label>
        <input
          type="number" value={nodeCount} onChange={(e) => setNodeCount(Number(e.target.value))}
          className="mb-3 w-full rounded border border-panel-border bg-void px-2 py-1 font-data text-sm text-bone"
        />
        <label className="mb-1 block text-xs text-muted">Scheduler</label>
        <select
          value={schedulerKind} onChange={(e) => setSchedulerKind(e.target.value)}
          className="mb-3 w-full rounded border border-panel-border bg-void px-2 py-1 text-sm text-bone"
        >
          <option value="fixed_dtc_baseline">Fixed DTC (baseline)</option>
          <option value="adaptive_rule_based">Adaptive — rule-based</option>
          <option value="adaptive_ml">Adaptive — ML</option>
        </select>
        <button onClick={handleStart} className="w-full rounded bg-signal py-1.5 text-sm font-medium text-void">
          Start simulation
        </button>
      </div>

      <div>
        <h2 className="mb-2 font-display text-sm tracking-wide text-bone">Controls</h2>
        <div className="flex flex-col gap-2">
          <button onClick={() => api.pauseSimulation().then(onStateChange)} className="rounded border border-panel-border py-1.5 text-sm text-bone">Pause</button>
          <button onClick={() => api.resumeSimulation().then(onStateChange)} className="rounded border border-panel-border py-1.5 text-sm text-bone">Resume</button>
        </div>
      </div>

      <div>
        <h2 className="mb-2 font-display text-sm tracking-wide text-bone">Inject scenario</h2>
        <div className="flex flex-col gap-2">
          {["low", "medium", "wildfire"].map((kind) => (
            <button
              key={kind} onClick={() => api.injectScenario(kind).then(onStateChange)}
              className="rounded border border-panel-border py-1.5 text-sm capitalize text-bone hover:border-signal"
            >
              {kind}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}