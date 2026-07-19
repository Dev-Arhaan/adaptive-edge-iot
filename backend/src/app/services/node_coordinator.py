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
            nodes=self._node_manager.all_nodes(),
            spatial_field=self._spatial_field,
            node_manager=self._node_manager,
            current_tick=current_tick,
        )

        self._node_manager.apply_battery_drain()
        self._node_manager.check_missed_heartbeats(current_tick, self._tick_duration_seconds)

        nodes_by_id = {n.id: n for n in self._node_manager.all_nodes()}
        for cluster in self._clusters.values():
            self._cluster_manager.reelect_head_if_needed(cluster, nodes_by_id)

    def all_nodes(self) -> list[Node]:
        return self._node_manager.all_nodes()

    def all_clusters(self) -> list[Cluster]:
        return list(self._clusters.values())

    def scheduling_history(self) -> SchedulingHistory:
        return self._scheduling_history


def create_default_virtual_forest(
    node_count: int = DEFAULT_NODE_COUNT,
    width: float = 1000,
    height: float = 1000,
    communication_radius: float = DEFAULT_COMMUNICATION_RADIUS,
    anchor_count: int = DEFAULT_ANCHOR_COUNT,
    tick_duration_seconds: int = 60,
    seed: int = 42,
) -> VirtualForest:
    """Composition root — tick_duration_seconds is threaded through both
    the scheduler and the forest from one place, so they can't silently
    desync the way two independent defaults could."""
    nodes = scatter_nodes(node_count, width, height, seed=seed)
    anchors = scatter_anchors(anchor_count, width, height, seed=seed)
    spatial_field = create_default_spatial_field(anchors, seed=seed)

    node_manager = NodeManager(battery_model=BatteryDrainModel())
    for node in nodes:
        node_manager.register_node(node)

    cluster_manager = ClusterManager(communication_radius=communication_radius)
    clusters = cluster_manager.form_clusters(nodes)

    scheduling_history = SchedulingHistory()
    scheduler = AdaptiveScheduler(
        risk_assessor=RuleBasedRiskAssessor(),
        policy=SchedulingPolicy(),
        history=scheduling_history,
        tick_duration_seconds=tick_duration_seconds,
    )

    return VirtualForest(
        spatial_field,
        node_manager,
        cluster_manager,
        clusters,
        scheduler,
        scheduling_history,
        tick_duration_seconds=tick_duration_seconds,
    )