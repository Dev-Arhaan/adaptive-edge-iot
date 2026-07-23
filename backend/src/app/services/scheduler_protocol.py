from typing import Protocol

from app.domain.node import Node
from app.services.node_manager import NodeManager
from app.services.spatial_field import SpatialField


class Scheduler(Protocol):
    """Implemented by AdaptiveScheduler and FixedIntervalScheduler.
    VirtualForest and the experiment runner depend only on this — swapping
    which scheduler is under test is a construction-time choice, never an
    orchestration-code change."""

    def step(
        self, nodes: list[Node], spatial_field: SpatialField, node_manager: NodeManager, current_tick: int
    ) -> None: ...