# tests/test_node_manager.py
from app.domain.enums import NodeHealth, SleepState
from app.services.generators.battery import BatteryDrainModel
from app.services.node_manager import NodeManager, scatter_nodes


def test_awake_node_drains_faster_than_asleep():
    awake_mgr = NodeManager(battery_model=BatteryDrainModel())
    awake_node = scatter_nodes(1, 100, 100, seed=1)[0]
    awake_mgr.register_node(awake_node)
    awake_mgr.wake(awake_node.id, tick=1)
    awake_mgr.apply_battery_drain()

    asleep_mgr = NodeManager(battery_model=BatteryDrainModel())
    asleep_node = scatter_nodes(1, 100, 100, seed=1)[0]
    asleep_mgr.register_node(asleep_node)
    asleep_mgr.apply_battery_drain()

    assert awake_mgr.get_node(awake_node.id).battery < asleep_mgr.get_node(asleep_node.id).battery


def test_node_dies_when_battery_depleted():
    node = scatter_nodes(1, 100, 100, seed=2)[0]
    node.battery = 0.01
    manager = NodeManager(battery_model=BatteryDrainModel())
    manager.register_node(node)
    manager.wake(node.id, tick=1)
    manager.apply_battery_drain()

    assert manager.get_node(node.id).health == NodeHealth.DEAD
    assert manager.get_node(node.id).sleep_state == SleepState.ASLEEP


def test_missed_heartbeat_flags_degraded():
    node = scatter_nodes(1, 100, 100, seed=3)[0]
    manager = NodeManager(battery_model=BatteryDrainModel())
    manager.register_node(node)  # never woken

    flagged = manager.check_missed_heartbeats(current_tick=100, tick_duration_seconds=60)
    assert node.id in flagged