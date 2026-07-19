from dataclasses import dataclass

from app.domain.enums import NodeHealth, SleepState


@dataclass
class Node:
    id: str
    cluster_id: str
    x: float
    y: float
    temperature: float = 20.0
    humidity: float = 50.0
    smoke: float = 0.0
    battery: float = 100.0
    sensing_interval_seconds: int = 300
    sleep_state: SleepState = SleepState.ASLEEP
    health: NodeHealth = NodeHealth.HEALTHY
    last_wake_tick: int = 0