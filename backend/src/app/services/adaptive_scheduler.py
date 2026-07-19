from app.domain.enums import NodeHealth, RiskLevel
from app.domain.node import Node
from app.domain.scheduling_decision import SchedulingDecision
from app.domain.sensor_reading import SensorReading
from app.services.node_manager import NodeManager
from app.services.risk_assessment.risk_assessor import RiskAssessor
from app.services.scheduling_history import SchedulingHistory
from app.services.scheduling_policy import SchedulingPolicy
from app.services.spatial_field import SpatialField


class AdaptiveScheduler:
    """Replaces fixed duty cycling with per-node intervals driven by
    RiskAssessor, plus same-tick emergency propagation to clusters.

    Two-phase per tick:
      Phase A - each node due for its own scheduled wake takes a fresh
                reading and is reassessed independently.
      Phase B - any cluster that produced an EMERGENCY reading in Phase A
                has its remaining members force-woken in the *same* tick —
                the alert doesn't wait a full cycle, which is the point of
                the emergency tier.

    Sleeping nodes are left untouched: their sensed values stay stale.
    That's intentional — a sleeping sensor genuinely doesn't know current
    conditions, which is the exact tradeoff being optimized.
    """

    def __init__(
        self,
        risk_assessor: RiskAssessor,
        policy: SchedulingPolicy,
        history: SchedulingHistory,
        tick_duration_seconds: int = 60,
    ):
        self._risk_assessor = risk_assessor
        self._policy = policy
        self._history = history
        self._tick_duration_seconds = tick_duration_seconds

    def step(
        self,
        nodes: list[Node],
        spatial_field: SpatialField,
        node_manager: NodeManager,
        current_tick: int,
    ) -> None:
        living = [n for n in nodes if n.health != NodeHealth.DEAD]
        woken: set[str] = set()
        emergency_clusters: set[str] = set()

        for node in living:
            if self._is_due(node, current_tick):
                level = self._wake_and_assess(
                    node, current_tick, spatial_field, node_manager, "scheduled"
                )
                woken.add(node.id)
                if level == RiskLevel.EMERGENCY:
                    emergency_clusters.add(node.cluster_id)
            else:
                node_manager.sleep(node.id)

        if not emergency_clusters:
            return

        by_cluster: dict[str, list[Node]] = {}
        for node in living:
            by_cluster.setdefault(node.cluster_id, []).append(node)

        for cluster_id in emergency_clusters:
            for node in by_cluster.get(cluster_id, []):
                if node.id in woken:
                    continue
                self._wake_and_assess(
                    node, current_tick, spatial_field, node_manager, "emergency_broadcast"
                )
                woken.add(node.id)

    def _is_due(self, node: Node, current_tick: int) -> bool:
        elapsed_seconds = (current_tick - node.last_wake_tick) * self._tick_duration_seconds
        return elapsed_seconds >= node.sensing_interval_seconds

    def _wake_and_assess(
        self,
        node: Node,
        current_tick: int,
        spatial_field: SpatialField,
        node_manager: NodeManager,
        trigger: str,
    ) -> RiskLevel:
        node_manager.wake(node.id, current_tick)

        local_env = spatial_field.sample_at(node.x, node.y)
        node.temperature = local_env.ambient_temperature
        node.humidity = local_env.ambient_humidity
        node.smoke = local_env.ambient_smoke

        assessment = self._risk_assessor.assess(
            SensorReading(temperature=node.temperature, humidity=node.humidity, smoke=node.smoke)
        )
        interval = self._policy.interval_for(assessment.level)
        node.sensing_interval_seconds = interval

        self._history.record(
            SchedulingDecision(
                tick=current_tick,
                node_id=node.id,
                cluster_id=node.cluster_id,
                risk_level=assessment.level,
                reason=assessment.reason,
                new_interval_seconds=interval,
                triggered_by=trigger,
            )
        )
        return assessment.level