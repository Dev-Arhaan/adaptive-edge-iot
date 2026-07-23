# tests/test_fixed_interval_scheduler.py
from app.domain.enums import RiskLevel
from app.domain.risk_assessment import RiskAssessment
from app.services.fixed_interval_scheduler import FixedIntervalScheduler
from app.services.node_manager import NodeManager, scatter_nodes
from app.services.generators.battery import BatteryDrainModel
from app.services.scheduling_history import SchedulingHistory
from app.services.spatial_field import create_default_spatial_field, scatter_anchors


class _AlwaysEmergency:
    def assess(self, reading):
        return RiskAssessment(level=RiskLevel.EMERGENCY, reason="forced")


def test_interval_never_changes_even_under_emergency_risk():
    nodes = scatter_nodes(3, 200, 200, seed=1)
    anchors = scatter_anchors(3, 200, 200, seed=1)
    field = create_default_spatial_field(anchors, seed=1)
    field.step()

    node_manager = NodeManager(battery_model=BatteryDrainModel())
    for n in nodes:
        node_manager.register_node(n)

    history = SchedulingHistory()
    scheduler = FixedIntervalScheduler(_AlwaysEmergency(), history, fixed_interval_seconds=300)
    scheduler.step(nodes, field, node_manager, current_tick=10)

    assert all(n.sensing_interval_seconds == 300 for n in nodes)
    assert len(history.all_decisions()) == len(nodes)
    assert all(d.risk_level == RiskLevel.EMERGENCY for d in history.all_decisions())