from typing import Protocol

from app.domain.risk_assessment import RiskAssessment
from app.domain.sensor_reading import SensorReading


class RiskAssessor(Protocol):
    """Strategy interface. RuleBasedRiskAssessor (Phase 4) and the future
    MLRiskAssessor (Phase 5) both implement this, so AdaptiveScheduler
    never changes when the risk source changes."""

    def assess(self, reading: SensorReading) -> RiskAssessment: ...