from app.domain.enums import RiskLevel

DEFAULT_INTERVALS_SECONDS: dict[RiskLevel, int] = {
    RiskLevel.LOW: 600,       # 10 min
    RiskLevel.MEDIUM: 300,    # 5 min
    RiskLevel.HIGH: 60,       # 1 min
    RiskLevel.EMERGENCY: 30,  # most aggressive — danger is still active
}


class SchedulingPolicy:
    """Risk -> sensing interval mapping, injectable so Phase 8 experiments
    can sweep these values without touching scheduler logic."""

    def __init__(self, intervals: dict[RiskLevel, int] | None = None):
        self._intervals = intervals or DEFAULT_INTERVALS_SECONDS

    def interval_for(self, level: RiskLevel) -> int:
        return self._intervals[level]