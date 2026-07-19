from dataclasses import dataclass

from app.domain.enums import RiskLevel


@dataclass(frozen=True)
class SchedulingDecision:
    tick: int
    node_id: str
    cluster_id: str
    risk_level: RiskLevel
    reason: str
    new_interval_seconds: int
    triggered_by: str  # "scheduled" | "emergency_broadcast"