from collections.abc import Callable
from dataclasses import dataclass

from app.domain.enums import RiskLevel
from app.domain.risk_assessment import RiskAssessment
from app.domain.sensor_reading import SensorReading


@dataclass(frozen=True)
class RiskRule:
    name: str
    level: RiskLevel
    predicate: Callable[[SensorReading], bool]


def _default_rules() -> list[RiskRule]:
    """Ordered most-severe-first; first match wins. Thresholds are tuned
    against Phase 2's SmokeGenerator range (baseline ~0.5, double digits
    under fire injection) — working estimates, revisit once Phase 8's
    scenario controller gives real calibration data."""
    return [
        RiskRule("smoke_critical", RiskLevel.EMERGENCY, lambda r: r.smoke >= 8.0),
        RiskRule(
            "smoke_high_or_hot_dry",
            RiskLevel.HIGH,
            lambda r: r.smoke >= 4.0 or (r.temperature >= 35 and r.humidity <= 25),
        ),
        RiskRule(
            "smoke_elevated_or_warm_dry",
            RiskLevel.MEDIUM,
            lambda r: r.smoke >= 1.5 or (r.temperature >= 30 and r.humidity <= 35),
        ),
    ]


class RuleBasedRiskAssessor:
    """Phase 4's risk source. Every assessment names the rule that fired,
    so scheduling decisions are explainable without Phase 6's SHAP."""

    def __init__(self, rules: list[RiskRule] | None = None):
        self._rules = rules or _default_rules()

    def assess(self, reading: SensorReading) -> RiskAssessment:
        for rule in self._rules:
            if rule.predicate(reading):
                return RiskAssessment(level=rule.level, reason=rule.name)
        return RiskAssessment(level=RiskLevel.LOW, reason="baseline_conditions")