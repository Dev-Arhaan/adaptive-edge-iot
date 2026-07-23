import time
from collections.abc import Callable
from dataclasses import dataclass

from app.domain.enums import NodeHealth, RiskLevel
from app.services.node_coordinator import create_default_virtual_forest
from app.services.scheduler_protocol import Scheduler
from app.services.scheduling_history import SchedulingHistory


@dataclass
class ExperimentResult:
    scenario_name: str
    scheduler_name: str
    node_count: int
    duration_ticks: int
    wall_clock_seconds: float
    total_wakes: int
    emergency_wakes: int
    emergency_broadcasts: int
    average_interval_seconds: float
    average_final_battery: float
    nodes_dead: int
    ignition_tick: int | None
    first_emergency_tick: int | None
    detection_latency_ticks: int | None


def run_experiment(
    scenario_name: str,
    scheduler_name: str,
    scheduler_factory: Callable[[SchedulingHistory, int], Scheduler],
    node_count: int,
    duration_ticks: int,
    seed: int,
    injector,
    ignition_tick: int | None,
) -> ExperimentResult:
    started = time.perf_counter()
    forest = create_default_virtual_forest(node_count=node_count, seed=seed, scheduler_factory=scheduler_factory)

    for tick in range(1, duration_ticks + 1):
        forest.step(current_tick=tick, fire_risk_by_anchor=injector.multiplier_at(tick))

    wall_clock_seconds = time.perf_counter() - started

    summary = forest.scheduling_history().summary()
    emergency_ticks = [d.tick for d in forest.scheduling_history().all_decisions() if d.risk_level == RiskLevel.EMERGENCY]
    first_emergency_tick = min(emergency_ticks) if emergency_ticks else None

    nodes = forest.all_nodes()
    detection_latency = (
        first_emergency_tick - ignition_tick
        if first_emergency_tick is not None and ignition_tick is not None
        else None
    )

    return ExperimentResult(
        scenario_name=scenario_name,
        scheduler_name=scheduler_name,
        node_count=node_count,
        duration_ticks=duration_ticks,
        wall_clock_seconds=wall_clock_seconds,
        total_wakes=summary["total_wakes"],
        emergency_wakes=summary["emergency_wakes"],
        emergency_broadcasts=summary["emergency_broadcasts"],
        average_interval_seconds=summary["average_interval_seconds"],
        average_final_battery=sum(n.battery for n in nodes) / len(nodes),
        nodes_dead=sum(1 for n in nodes if n.health == NodeHealth.DEAD),
        ignition_tick=ignition_tick,
        first_emergency_tick=first_emergency_tick,
        detection_latency_ticks=detection_latency,
    )