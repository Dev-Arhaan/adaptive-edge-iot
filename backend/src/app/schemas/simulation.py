from pydantic import BaseModel


class NodeSchema(BaseModel):
    id: str
    cluster_id: str
    x: float
    y: float
    temperature: float
    humidity: float
    smoke: float
    battery: float
    sensing_interval_seconds: int
    sleep_state: str
    health: str
    last_risk_level: str | None = None


class ClusterSchema(BaseModel):
    id: str
    center_x: float
    center_y: float
    node_ids: list[str]
    head_node_id: str | None


class SchedulingDecisionSchema(BaseModel):
    tick: int
    node_id: str
    cluster_id: str
    risk_level: str
    reason: str
    new_interval_seconds: int
    triggered_by: str


class SimulationStateResponse(BaseModel):
    started: bool
    running: bool | None = None
    tick: int | None = None
    node_count: int | None = None
    cluster_count: int | None = None
    average_battery: float | None = None
    history_summary: dict | None = None


class StartSimulationRequest(BaseModel):
    node_count: int = 150
    scheduler_kind: str = "adaptive_rule_based"
    seed: int = 42


class ScenarioInjectionRequest(BaseModel):
    scenario_kind: str  # "low" | "medium" | "wildfire"

class NodeEventSchema(BaseModel):
    tick: int
    node_id: str
    event_type: str
    detail: str


class MetricsSnapshotSchema(BaseModel):
    tick: int
    average_interval_seconds: float
    total_wakes: int
    emergency_wakes_since_last: int
    average_battery: float