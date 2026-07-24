"use client";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import type { ExplanationResponse } from "@/lib/api";

export function ShapWaterfall({ explanation }: { explanation: ExplanationResponse }) {
  const data = explanation.contributions.map((c) => ({ name: c.feature_name, shap_value: Number(c.shap_value.toFixed(3)) }));

  return (
    <div className="rounded border border-panel-border bg-panel p-3">
      <h3 className="mb-1 font-display text-sm text-bone">
        Why: {explanation.predicted_level} ({(explanation.confidence * 100).toFixed(0)}% confidence)
      </h3>
      <p className="mb-2 font-data text-xs text-muted">Base value {explanation.base_value.toFixed(3)}</p>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
          <CartesianGrid stroke="#333B2C" strokeDasharray="3 3" />
          <XAxis type="number" stroke="#8B9184" fontSize={11} />
          <YAxis type="category" dataKey="name" stroke="#8B9184" fontSize={11} width={90} />
          <Tooltip contentStyle={{ background: "#1E2419", border: "1px solid #333B2C" }} />
          <Bar dataKey="shap_value" radius={[0, 3, 3, 0]}>
            {data.map((entry, index) => <Cell key={index} fill={entry.shap_value >= 0 ? "#E4572E" : "#6E9B7B"} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="mt-1 text-xs text-muted">Ember = pushes toward {explanation.predicted_level}, moss = pushes away</p>
    </div>
  );
}