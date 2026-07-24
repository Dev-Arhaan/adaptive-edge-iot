from dataclasses import dataclass


@dataclass(frozen=True)
class NodeEvent:
    tick: int
    node_id: str
    event_type: str  # "became_degraded" | "died"
    detail: str