# tests/test_node_manager_events.py
from app.services.generators.battery import BatteryDrainModel
from app.services.node_manager import NodeManager, scatter_nodes


def test_battery_depletion_emits_died_event():
    node = scatter_nodes(1, 100, 100, seed=1)[0]
    node.battery = 0.01
    manager = NodeManager(battery_model=BatteryDrainModel())
    manager.register_node(node)
    manager.wake(node.id, tick=1)

    manager.apply_battery_drain(current_tick=5)

    assert any(e.event_type == "died" and e.tick == 5 for e in manager.events())


def test_healthy_node_emits_no_events():
    node = scatter_nodes(1, 100, 100, seed=2)[0]
    manager = NodeManager(battery_model=BatteryDrainModel())
    manager.register_node(node)

    manager.apply_battery_drain(current_tick=1)

    assert manager.events() == []