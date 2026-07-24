"use client";
import { useMemo, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { api, ExplanationResponse, NodeState } from "@/lib/api";
import { ShapWaterfall } from "./ShapWaterfall";

const RISK_COLORS: Record<string, string> = { low: "#6E9B7B", medium: "#D9A441", high: "#E4572E", emergency: "#C6362B" };

export function RiskDashboard({ nodes }: { nodes: NodeState[] }) {
  const [temperature, setTemperature] = useState(30);
  const [humidity, setHumidity] = useState(25);
  const [smoke, setSmoke] = useState(5);
  const [explanation, setExplanation] = useState<ExplanationResponse | null>(null);

  const distribution = useMemo(() => {
    const counts: Record<string, number> = { low: 0, medium: 0, high: 0, emergency: 0 };
    nodes.forEach((n) => { if (n.last_risk_level) counts[n.last_risk_level] += 1; });
    return Object.entries(counts).filter(([, count]) => count > 0).map(([level, count]) => ({ level, count }));
  }, [nodes]);

  async function handlePredict() {
    const result = await api.predictRisk({ temperature, humidity, smoke });
    setExplanation(await api.explainPrediction(result.id));
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <div className="rounded border border-panel-border bg-panel p-3">
        <h3 className="mb-2 font-display text-sm text-bone">Live risk distribution</h3>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie data={distribution} dataKey="count" nameKey="level" outerRadius={70}>
              {distribution.map((entry) => <Cell key={entry.level} fill={RISK_COLORS[entry.level]} />)}
            </Pie>
            <Tooltip contentStyle={{ background: "#1E2419", border: "1px solid #333B2C" }} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="rounded border border-panel-border bg-panel p-3">
        <h3 className="mb-2 font-display text-sm text-bone">Test a reading</h3>
        <div className="mb-2 grid grid-cols-3 gap-2 font-data text-xs">
          <label className="flex flex-col gap-1 text-muted">Temp °C
            <input type="number" value={temperature} onChange={(e) => setTemperature(Number(e.target.value))} className="rounded border border-panel-border bg-void px-2 py-1 text-bone" />
          </label>
          <label className="flex flex-col gap-1 text-muted">Humidity %
            <input type="number" value={humidity} onChange={(e) => setHumidity(Number(e.target.value))} className="rounded border border-panel-border bg-void px-2 py-1 text-bone" />
          </label>
          <label className="flex flex-col gap-1 text-muted">Smoke
            <input type="number" value={smoke} onChange={(e) => setSmoke(Number(e.target.value))} className="rounded border border-panel-border bg-void px-2 py-1 text-bone" />
          </label>
        </div>
        <button onClick={handlePredict} className="w-full rounded bg-signal py-1.5 text-sm font-medium text-void">
          Predict &amp; explain
        </button>
      </div>

      {explanation && <div className="md:col-span-2"><ShapWaterfall explanation={explanation} /></div>}
    </div>
  );
}