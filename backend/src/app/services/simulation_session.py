from app.core.model_registry import get_ml_risk_assessor
from app.domain.node_event import NodeEvent
from app.services.adaptive_scheduler import AdaptiveScheduler
from app.services.fixed_interval_scheduler import FixedIntervalScheduler
from app.services.metrics_time_series import MetricsSnapshot, MetricsTimeSeries
from app.services.node_coordinator import VirtualForest, create_default_virtual_forest
from app.services.risk_assessment.rule_based_risk_assessor import RuleBasedRiskAssessor
from app.services.scenarios.constant_risk_injector import ConstantRiskInjector
from app.services.scenarios.fire_episode_injector import FireEpisodeInjector
from app.services.scheduling_policy import SchedulingPolicy

SCHEDULER_FACTORIES = {
    "fixed_dtc_baseline": lambda h, td: FixedIntervalScheduler(RuleBasedRiskAssessor(), h, tick_duration_seconds=td),
    "adaptive_rule_based": lambda h, td: AdaptiveScheduler(RuleBasedRiskAssessor(), SchedulingPolicy(), h, td),
    "adaptive_ml": lambda h, td: AdaptiveScheduler(get_ml_risk_assessor(), SchedulingPolicy(), h, td),
}


class SimulationSessionManager:
    def __init__(self):
        self._forest: VirtualForest | None = None
        self._anchor_ids: list[str] = []
        self._tick = 0
        self._running = False
        self._injector = None
        self._metrics = MetricsTimeSeries()
        self._last_emergency_wakes = 0

    @property
    def is_running(self) -> bool:
        return self._running and self._forest is not None

    def start(self, node_count: int = 150, scheduler_kind: str = "adaptive_rule_based", seed: int = 42) -> None:
        factory = SCHEDULER_FACTORIES[scheduler_kind]
        self._forest = create_default_virtual_forest(node_count=node_count, seed=seed, scheduler_factory=factory)
        self._anchor_ids = self._forest.anchor_ids()
        self._tick = 0
        self._injector = ConstantRiskInjector(self._anchor_ids, multiplier=1.0)
        self._metrics = MetricsTimeSeries()
        self._last_emergency_wakes = 0
        self._running = True

    def pause(self) -> None:
        self._running = False

    def resume(self) -> None:
        if self._forest is not None:
            self._running = True

    def inject_scenario(self, kind: str) -> None:
        if self._forest is None:
            raise RuntimeError("Start a simulation before injecting a scenario")
        if kind == "low":
            self._injector = ConstantRiskInjector(self._anchor_ids, multiplier=1.0)
        elif kind == "medium":
            self._injector = ConstantRiskInjector(self._anchor_ids, multiplier=3.0)
        elif kind == "wildfire":
            self._injector = FireEpisodeInjector(self._anchor_ids, episode_length_ticks=720, peak_multiplier=25.0, fire_probability=1.0)
        else:
            raise ValueError(f"Unknown scenario kind: {kind}")

    def step_once(self) -> None:
        if not self.is_running:
            return
        self._tick += 1
        self._forest.step(current_tick=self._tick, fire_risk_by_anchor=self._injector.multiplier_at(self._tick))
        self._record_metrics_snapshot()

    def _record_metrics_snapshot(self) -> None:
        summary = self._forest.scheduling_history().summary()
        nodes = self._forest.all_nodes()
        emergency_delta = summary["emergency_wakes"] - self._last_emergency_wakes
        self._last_emergency_wakes = summary["emergency_wakes"]
        self._metrics.record(
            MetricsSnapshot(
                tick=self._tick,
                average_interval_seconds=summary["average_interval_seconds"],
                total_wakes=summary["total_wakes"],
                emergency_wakes_since_last=emergency_delta,
                average_battery=sum(n.battery for n in nodes) / len(nodes) if nodes else 0.0,
            )
        )

    def snapshot(self) -> dict:
        if self._forest is None:
            return {"started": False}
        nodes = self._forest.all_nodes()
        return {
            "started": True, "running": self._running, "tick": self._tick,
            "node_count": len(nodes), "cluster_count": len(self._forest.all_clusters()),
            "average_battery": sum(n.battery for n in nodes) / len(nodes) if nodes else 0.0,
            "history_summary": self._forest.scheduling_history().summary(),
        }

    def forest(self) -> VirtualForest:
        if self._forest is None:
            raise RuntimeError("Simulation not started")
        return self._forest

    def metrics_timeseries(self) -> list[MetricsSnapshot]:
        return self._metrics.all_points()

    def node_events(self) -> list[NodeEvent]:
        return self._forest.node_events() if self._forest else []


session_manager = SimulationSessionManager()