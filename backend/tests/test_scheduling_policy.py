# tests/test_scheduling_policy.py
from app.domain.enums import RiskLevel
from app.services.scheduling_policy import SchedulingPolicy


def test_emergency_interval_is_shortest_and_low_is_longest():
    policy = SchedulingPolicy()
    intervals = {level: policy.interval_for(level) for level in RiskLevel}
    assert intervals[RiskLevel.EMERGENCY] == min(intervals.values())
    assert intervals[RiskLevel.LOW] == max(intervals.values())