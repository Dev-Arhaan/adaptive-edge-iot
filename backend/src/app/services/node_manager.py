import numpy as np

from app.domain.enums import NodeHealth, SleepState
from app.domain.node import Node
from app.services.generators.battery import BatteryDrainModel

DEFAULT_NODE_COUNT = 150  # matches "hundreds of nodes" goal; keeps O(n^2) clustering trivial


class NodeManager:
    """Owns the authoritative set of Node domain objects: creation, sleep/
    wake transitions, battery tracking, and health derived from battery +
    heartbeat compliance. Does not decide *when* nodes should wake — that's
    Phase 4's Adaptive Scheduler; NodeManager just applies whatever
    sleep_state / sensing_interval it's told and tracks the consequences.
    """

    def __init__(self, battery_model: BatteryDrainModel, heartbeat_grace_multiplier: float = 2.0):
        self._nodes: dict[str, Node] = {}
        self._battery_model = battery_model
        self._heartbeat_grace_multiplier = heartbeat_grace_multiplier

    def register_node(self, node: Node) -> None:
        self._nodes[node.id] = node

    def get_node(self, node_id: str) -> Node:
        return self._nodes[node_id]

    def all_nodes(self) -> list[Node]:
        return list(self._nodes.values())

    def wake(self, node_id: str, tick: int) -> None:
        node = self._nodes[node_id]
        if node.health == NodeHealth.DEAD:
            return
        node.sleep_state = SleepState.AWAKE
        node.last_wake_tick = tick

    def sleep(self, node_id: str) -> None:
        node = self._nodes[node_id]
        if node.health == NodeHealth.DEAD:
            return
        node.sleep_state = SleepState.ASLEEP

    def apply_battery_drain(self) -> None:
        for node in self._nodes.values():
            if node.health == NodeHealth.DEAD:
                continue
            is_awake = node.sleep_state == SleepState.AWAKE
            node.battery = self._battery_model.drain(node.battery, is_awake)
            self._update_health_from_battery(node)

    def _update_health_from_battery(self, node: Node) -> None:
        if node.battery <= 0:
            node.health = NodeHealth.DEAD
            node.sleep_state = SleepState.ASLEEP
        elif node.battery <= 15:
            node.health = NodeHealth.DEGRADED
        else:
            node.health = NodeHealth.HEALTHY

    def check_missed_heartbeats(self, current_tick: int, tick_duration_seconds: int) -> list[str]:
        """Flags nodes DEGRADED if they haven't woken within
        grace_multiplier x their own sensing_interval. Note: with no
        scheduler yet (Phase 4), this will flag everything — that's
        expected until something actually starts waking nodes."""
        flagged = []
        for node in self._nodes.values():
            if node.health == NodeHealth.DEAD:
                continue
            expected_ticks = max(1, node.sensing_interval_seconds // tick_duration_seconds)
            elapsed = current_tick - node.last_wake_tick
            if elapsed > expected_ticks * self._heartbeat_grace_multiplier:
                node.health = NodeHealth.DEGRADED
                flagged.append(node.id)
        return flagged


def scatter_nodes(count: int, width: float, height: float, seed: int = 42) -> list[Node]:
    """Deterministically scatters N stationary nodes — fixed forest
    sensors, so this runs once at setup, never per tick."""
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0, width, size=count)
    ys = rng.uniform(0, height, size=count)
    return [
        Node(id=f"node-{i}", cluster_id="", x=float(x), y=float(y))
        for i, (x, y) in enumerate(zip(xs, ys))
    ]