from dataclasses import dataclass, field


@dataclass
class Cluster:
    id: str
    center_x: float
    center_y: float
    node_ids: list[str] = field(default_factory=list)
    head_node_id: str | None = None
