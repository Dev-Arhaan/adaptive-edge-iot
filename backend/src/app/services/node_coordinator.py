from app.domain.node_event import NodeEvent
from app.domain.cluster import Cluster
from app.domain.node import Node
from app.services.adaptive_scheduler import AdaptiveScheduler
from app.services.cluster_manager import ClusterManager
from app.services.generators.battery import BatteryDrainModel
from app.services.node_manager import DEFAULT_NODE_COUNT, NodeManager, scatter_nodes
from app.services.risk_assessment.rule_based_risk_assessor import RuleBasedRiskAssessor
from app.services.scheduling_history import SchedulingHistory
from app.services.scheduling_policy import SchedulingPolicy
from app.services.spatial_field import SpatialField, create_default_spatial_field, scatter_anchors

DEFAULT_COMMUNICATION_RADIUS = 150
DEFAULT_ANCHOR_COUNT = 5


class VirtualForest:
    """Coordinates the environment layer (SpatialField), device state
    (NodeManager), topology (ClusterManager), and now the adaptive
    scheduler into one steppable simulation."""

    def __init__(
        self,
        spatial_field: SpatialField,
        node_manager: NodeManager,
        cluster_manager: ClusterManager,
        clusters: list[Cluster],
        scheduler: AdaptiveScheduler,
        scheduling_history: SchedulingHistory,
        tick_duration_seconds: int = 60,
    ):
        self._spatial_field = spatial_field
        self._node_manager = node_manager
        self._cluster_manager = cluster_manager
        self._clusters = {c.id: c for c in clusters}
        self._scheduler = scheduler
        self._scheduling_history = scheduling_history
        self._tick_duration_seconds = tick_duration_seconds

    def step(self, current_tick: int, fire_risk_by_anchor: dict[str, float] | None = None) -> None:
        self._spatial_field.step(fire_risk_by_anchor)

        self._scheduler.step(
            nodes=self._node_manager.all_nodes(), spatial_field=self._spatial_field,
            node_manager=self._node_manager, current_tick=current_tick,
        )

        self._node_manager.apply_battery_drain(current_tick)
        self._node_manager.check_missed_heartbeats(current_tick, self._tick_duration_seconds)

        nodes_by_id = {n.id: n for n in self._node_manager.all_nodes()}
        for cluster in self._clusters.values():
            self._cluster_manager.reelect_head_if_needed(cluster, nodes_by_id)

    def node_events(self) -> list[NodeEvent]:
        return self._node_manager.events()

    def all_nodes(self) -> list[Node]:
        return self._node_manager.all_nodes()

    def all_clusters(self) -> list[Cluster]:
        return list(self._clusters.values())

    def scheduling_history(self) -> SchedulingHistory:
        return self._scheduling_history
    
    def anchor_ids(self) -> list[str]:
        return self._spatial_field.anchor_ids()


from collections.abc import Callable

from app.services.scheduler_protocol import Scheduler

def create_default_virtual_forest(
    node_count: int = DEFAULT_NODE_COUNT,
    width: float = 1000,
    height: float = 1000,
    communication_radius: float = DEFAULT_COMMUNICATION_RADIUS,
    anchor_count: int = DEFAULT_ANCHOR_COUNT,
    tick_duration_seconds: int = 60,
    seed: int = 42,
    scheduler_factory: Callable[[SchedulingHistory, int], Scheduler] | None = None,
) -> VirtualForest:
    """Composition root. scheduler_factory takes (history, tick_duration_seconds)
    — threading tick_duration_seconds through it, rather than letting a
    scheduler default it independently, closes the exact desync gap Phase 4
    already had to fix once. Defaults to Phase 4's rule-based adaptive
    setup for full backward compatibility with earlier phases."""
    nodes = scatter_nodes(node_count, width, height, seed=seed)
    anchors = scatter_anchors(anchor_count, width, height, seed=seed)
    spatial_field = create_default_spatial_field(anchors, seed=seed)

    node_manager = NodeManager(battery_model=BatteryDrainModel())
    for node in nodes:
        node_manager.register_node(node)

    cluster_manager = ClusterManager(communication_radius=communication_radius)
    clusters = cluster_manager.form_clusters(nodes)

    scheduling_history = SchedulingHistory()
    if scheduler_factory is None:
        scheduler = AdaptiveScheduler(
            RuleBasedRiskAssessor(), SchedulingPolicy(), scheduling_history, tick_duration_seconds
        )
    else:
        scheduler = scheduler_factory(scheduling_history, tick_duration_seconds)

    return VirtualForest(
        spatial_field, node_manager, cluster_manager, clusters, scheduler, scheduling_history,
        tick_duration_seconds=tick_duration_seconds,
    )