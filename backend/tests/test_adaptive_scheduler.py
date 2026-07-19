# tests/test_adaptive_scheduler.py
from app.domain.enums import RiskLevel
from app.domain.risk_assessment import RiskAssessment
from app.domain.sensor_reading import SensorReading
from app.services.adaptive_scheduler import AdaptiveScheduler
from app.services.cluster_manager import ClusterManager
from app.services.generators.battery import BatteryDrainModel
from app.services.node_manager import NodeManager, scatter_nodes
from app.services.risk_assessment.rule_based_risk_assessor import RuleBasedRiskAssessor
from app.services.scheduling_history import SchedulingHistory
from app.services.scheduling_policy import SchedulingPolicy
from app.services.spatial_field import create_default_spatial_field, scatter_anchors


class _AlwaysEmergencyAssessor:
    def assess(self, reading: SensorReading) -> RiskAssessment:
        return RiskAssessment(level=RiskLevel.EMERGENCY, reason="test_forced")


def _build(node_count=6, radius=200, seed=1):
    nodes = scatter_nodes(node_count, 200, 200, seed=seed)
    anchors = scatter_anchors(3, 200, 200, seed=seed)
    field = create_default_spatial_field(anchors, seed=seed)
    node_manager = NodeManager(battery_model=BatteryDrainModel())
    for n in nodes:
        node_manager.register_node(n)
    ClusterManager(communication_radius=radius).form_clusters(nodes)
    return nodes, field, node_manager


def test_due_node_wakes_and_gets_reassigned_interval():
    nodes, field, node_manager = _build()
    field.step()
    history = SchedulingHistory()
    scheduler = AdaptiveScheduler(RuleBasedRiskAssessor(), SchedulingPolicy(), history)

    scheduler.step(nodes, field, node_manager, current_tick=10)

    assert len(history.all_decisions()) > 0


def test_emergency_propagates_to_whole_cluster_same_tick():
    nodes, field, node_manager = _build(node_count=4, radius=1000)
    field.step()

    for i, n in enumerate(nodes):
        n.cluster_id = "cluster-shared"
        n.last_wake_tick = -1000 if i == 0 else 10  # only node 0 is naturally due at tick=10

    history = SchedulingHistory()
    scheduler = AdaptiveScheduler(_AlwaysEmergencyAssessor(), SchedulingPolicy(), history)
    scheduler.step(nodes, field, node_manager, current_tick=10)

    broadcasts = [d for d in history.all_decisions() if d.triggered_by == "emergency_broadcast"]
    assert len(broadcasts) == 3  # the other 3 cluster members, woken same-tick