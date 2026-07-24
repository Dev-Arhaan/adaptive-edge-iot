from fastapi import APIRouter, Depends

from app.core.auth import require_auth
from app.schemas.simulation import (
    ClusterSchema, NodeSchema, ScenarioInjectionRequest, SchedulingDecisionSchema,
    SimulationStateResponse, StartSimulationRequest, NodeEventSchema, MetricsSnapshotSchema
)
from app.services.simulation_session import session_manager

router = APIRouter(prefix="/simulation", tags=["simulation"], dependencies=[Depends(require_auth)])


@router.post("/start", response_model=SimulationStateResponse)
def start_simulation(payload: StartSimulationRequest) -> SimulationStateResponse:
    session_manager.start(node_count=payload.node_count, scheduler_kind=payload.scheduler_kind, seed=payload.seed)
    return SimulationStateResponse(**session_manager.snapshot())


@router.post("/pause", response_model=SimulationStateResponse)
def pause_simulation() -> SimulationStateResponse:
    session_manager.pause()
    return SimulationStateResponse(**session_manager.snapshot())


@router.post("/resume", response_model=SimulationStateResponse)
def resume_simulation() -> SimulationStateResponse:
    session_manager.resume()
    return SimulationStateResponse(**session_manager.snapshot())


@router.post("/inject-scenario", response_model=SimulationStateResponse)
def inject_scenario(payload: ScenarioInjectionRequest) -> SimulationStateResponse:
    session_manager.inject_scenario(payload.scenario_kind)
    return SimulationStateResponse(**session_manager.snapshot())


@router.get("/state", response_model=SimulationStateResponse)
def get_state() -> SimulationStateResponse:
    return SimulationStateResponse(**session_manager.snapshot())


@router.get("/nodes", response_model=list[NodeSchema])
def get_nodes() -> list[NodeSchema]:
    forest = session_manager.forest()
    latest_decisions = forest.scheduling_history().latest_by_node()
    return [
        NodeSchema(
            id=n.id, cluster_id=n.cluster_id, x=n.x, y=n.y, temperature=n.temperature,
            humidity=n.humidity, smoke=n.smoke, battery=n.battery,
            sensing_interval_seconds=n.sensing_interval_seconds,
            sleep_state=n.sleep_state.value, health=n.health.value,
            last_risk_level=latest_decisions[n.id].risk_level.value if n.id in latest_decisions else None,
        )
        for n in forest.all_nodes()
    ]


@router.get("/clusters", response_model=list[ClusterSchema])
def get_clusters() -> list[ClusterSchema]:
    forest = session_manager.forest()
    return [
        ClusterSchema(id=c.id, center_x=c.center_x, center_y=c.center_y, node_ids=c.node_ids, head_node_id=c.head_node_id)
        for c in forest.all_clusters()
    ]


@router.get("/scheduling-history", response_model=list[SchedulingDecisionSchema])
def get_scheduling_history(limit: int = 100) -> list[SchedulingDecisionSchema]:
    decisions = session_manager.forest().scheduling_history().all_decisions()[-limit:]
    return [
        SchedulingDecisionSchema(
            tick=d.tick, node_id=d.node_id, cluster_id=d.cluster_id, risk_level=d.risk_level.value,
            reason=d.reason, new_interval_seconds=d.new_interval_seconds, triggered_by=d.triggered_by,
        )
        for d in decisions
    ]

@router.get("/events", response_model=list[NodeEventSchema])
def get_node_events(limit: int = 100) -> list[NodeEventSchema]:
    events = session_manager.node_events()[-limit:]
    return [NodeEventSchema(tick=e.tick, node_id=e.node_id, event_type=e.event_type, detail=e.detail) for e in events]


@router.get("/metrics-timeseries", response_model=list[MetricsSnapshotSchema])
def get_metrics_timeseries() -> list[MetricsSnapshotSchema]:
    return [
        MetricsSnapshotSchema(
            tick=m.tick, average_interval_seconds=m.average_interval_seconds, total_wakes=m.total_wakes,
            emergency_wakes_since_last=m.emergency_wakes_since_last, average_battery=m.average_battery,
        )
        for m in session_manager.metrics_timeseries()
    ]