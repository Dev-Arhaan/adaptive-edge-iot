const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export type NodeState = {
  id: string; cluster_id: string; x: number; y: number;
  temperature: number; humidity: number; smoke: number; battery: number;
  sensing_interval_seconds: number; sleep_state: string; health: string;
  last_risk_level: string | null;
};

export type ClusterState = {
  id: string; center_x: number; center_y: number; node_ids: string[]; head_node_id: string | null;
};

export type SimulationState = {
  started: boolean; running?: boolean; tick?: number; node_count?: number;
  cluster_count?: number; average_battery?: number; history_summary?: Record<string, number>;
};

function authHeaders(): HeadersInit {
  const token = typeof window !== "undefined" ? window.localStorage.getItem("dashboard_token") : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...authHeaders(), ...(init?.headers ?? {}) },
  });
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

export const api = {
  login: (passphrase: string) =>
    request<{ token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ passphrase }) }),
  startSimulation: (nodeCount: number, schedulerKind: string) =>
    request<SimulationState>("/simulation/start", {
      method: "POST", body: JSON.stringify({ node_count: nodeCount, scheduler_kind: schedulerKind }),
    }),
  pauseSimulation: () => request<SimulationState>("/simulation/pause", { method: "POST" }),
  resumeSimulation: () => request<SimulationState>("/simulation/resume", { method: "POST" }),
  injectScenario: (scenarioKind: string) =>
    request<SimulationState>("/simulation/inject-scenario", {
      method: "POST", body: JSON.stringify({ scenario_kind: scenarioKind }),
    }),
  getState: () => request<SimulationState>("/simulation/state"),
  getNodes: () => request<NodeState[]>("/simulation/nodes"),
  getClusters: () => request<ClusterState[]>("/simulation/clusters"),
  getSchedulingHistory: (limit = 100) => request<SchedulingDecision[]>(`/simulation/scheduling-history?limit=${limit}`),
  getEvents: (limit = 100) => request<NodeEvent[]>(`/simulation/events?limit=${limit}`),
  getMetricsTimeSeries: () => request<MetricsSnapshot[]>("/simulation/metrics-timeseries"),
  predictRisk: (reading: { temperature: number; humidity: number; smoke: number }) =>
    request<RiskPredictionResponse>("/predictions/risk", { method: "POST", body: JSON.stringify(reading) }),
  explainPrediction: (id: number) => request<ExplanationResponse>(`/predictions/${id}/explain`),
};

export type SchedulingDecision = {
  tick: number; node_id: string; cluster_id: string; risk_level: string;
  reason: string; new_interval_seconds: number; triggered_by: string;
};

export type NodeEvent = { tick: number; node_id: string; event_type: string; detail: string };

export type MetricsSnapshot = {
  tick: number; average_interval_seconds: number; total_wakes: number;
  emergency_wakes_since_last: number; average_battery: number;
};

export type RiskPredictionResponse = { id: number; level: string; confidence: number; reason: string };

export type ExplanationResponse = {
  prediction_id: number; predicted_level: string; confidence: number; base_value: number;
  contributions: { feature_name: string; value: number; shap_value: number }[];
};