from app.domain.enums import RiskLevel
from app.domain.scheduling_decision import SchedulingDecision


class SchedulingHistory:
    """Append-only log of every scheduling decision plus summary metrics —
    what Phase 8's fixed-vs-adaptive comparison and Phase 9's figures
    consume directly. Kept separate so AdaptiveScheduler stays focused on
    deciding, not reporting."""

    def __init__(self):
        self._decisions: list[SchedulingDecision] = []

    def record(self, decision: SchedulingDecision) -> None:
        self._decisions.append(decision)

    def all_decisions(self) -> list[SchedulingDecision]:
        return list(self._decisions)

    def summary(self) -> dict[str, float | int]:
        total = len(self._decisions)
        if total == 0:
            return {
                "total_wakes": 0,
                "emergency_wakes": 0,
                "emergency_broadcasts": 0,
                "average_interval_seconds": 0.0,
            }
        return {
            "total_wakes": total,
            "emergency_wakes": sum(1 for d in self._decisions if d.risk_level == RiskLevel.EMERGENCY),
            "emergency_broadcasts": sum(
                1 for d in self._decisions if d.triggered_by == "emergency_broadcast"
            ),
            "average_interval_seconds": sum(d.new_interval_seconds for d in self._decisions) / total,
        }
    def latest_by_node(self) -> dict[str, SchedulingDecision]:
        latest: dict[str, SchedulingDecision] = {}
        for decision in self._decisions:
            latest[decision.node_id] = decision  # later entries overwrite earlier ones
        return latest