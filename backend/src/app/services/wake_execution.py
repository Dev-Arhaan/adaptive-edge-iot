from app.domain.node import Node
from app.domain.sensor_reading import SensorReading
from app.services.node_manager import NodeManager
from app.services.spatial_field import SpatialField


def wake_and_sample(
    node: Node, current_tick: int, spatial_field: SpatialField, node_manager: NodeManager
) -> SensorReading:
    """Wakes a node and refreshes its sensed values. Shared by every
    Scheduler implementation so AdaptiveScheduler and FixedIntervalScheduler
    sample the environment identically — the fixed-vs-adaptive comparison
    would be unfair otherwise."""
    node_manager.wake(node.id, current_tick)
    local_env = spatial_field.sample_at(node.x, node.y)
    node.temperature = local_env.ambient_temperature
    node.humidity = local_env.ambient_humidity
    node.smoke = local_env.ambient_smoke
    return SensorReading(temperature=node.temperature, humidity=node.humidity, smoke=node.smoke)