# tests/test_rule_based_risk_assessor.py
from app.domain.enums import RiskLevel
from app.domain.sensor_reading import SensorReading
from app.services.risk_assessment.rule_based_risk_assessor import RuleBasedRiskAssessor


def test_baseline_conditions_are_low_risk():
    assessor = RuleBasedRiskAssessor()
    result = assessor.assess(SensorReading(temperature=22, humidity=55, smoke=0.4))
    assert result.level == RiskLevel.LOW


def test_high_smoke_is_emergency():
    assessor = RuleBasedRiskAssessor()
    result = assessor.assess(SensorReading(temperature=28, humidity=40, smoke=9.0))
    assert result.level == RiskLevel.EMERGENCY
    assert result.reason == "smoke_critical"


def test_hot_dry_without_smoke_is_high():
    assessor = RuleBasedRiskAssessor()
    result = assessor.assess(SensorReading(temperature=37, humidity=20, smoke=0.5))
    assert result.level == RiskLevel.HIGH