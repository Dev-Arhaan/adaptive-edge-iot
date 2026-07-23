from app.domain.enums import NodeHealth
from app.domain.node import Node
from app.domain.scheduling_decision import SchedulingDecision
from app.services.node_manager import NodeManager
from app.services.risk_assessment.risk_assessor import RiskAssessor
from app.services.scheduling_history import SchedulingHistory
from app.services.spatial_field import SpatialField
from app.services.wake_execution import wake_and_sample


class FixedIntervalScheduler:
    """Baseline mirroring the original DTC protocol: fixed rotation (300s
    by default), deep sleep in between, no adaptive behavior. Still
    assesses risk on every wake and records it — not to influence
    scheduling (interval never changes), but so Phase 8 can measure a fair
    detection-latency comparison against AdaptiveScheduler's actual
    behavior. Implements the same Scheduler protocol, so VirtualForest and
    the experiment runner don't need to know which scheduler they hold.
    """

    def __init__(
        self,
        risk_assessor: RiskAssessor,
        history: SchedulingHistory,
        tick_duration_seconds: int = 60,
        fixed_interval_seconds: int = 300,
    ):
        self._risk_assessor = risk_assessor
        self._history = history
        self._tick_duration_seconds = tick_duration_seconds
        self._fixed_interval_seconds = fixed_interval_seconds

    def step(
        self, nodes: list[Node], spatial_field: SpatialField, node_manager: NodeManager, current_tick: int
    ) -> None:
        for node in nodes:
            if node.health == NodeHealth.DEAD:
                continue

            elapsed_seconds = (current_tick - node.last_wake_tick) * self._tick_duration_seconds
            if elapsed_seconds < self._fixed_interval_seconds:
                node_manager.sleep(node.id)
                continue

            reading = wake_and_sample(node, current_tick, spatial_field, node_manager)
            assessment = self._risk_assessor.assess(reading)
            node.sensing_interval_seconds = self._fixed_interval_seconds  # never adapted — that's the point

            self._history.record(
                SchedulingDecision(
                    tick=current_tick,
                    node_id=node.id,
                    cluster_id=node.cluster_id,
                    risk_level=assessment.level,
                    reason=assessment.reason,
                    new_interval_seconds=self._fixed_interval_seconds,
                    triggered_by="scheduled",
                )
            )