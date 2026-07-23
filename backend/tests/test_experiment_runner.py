# tests/test_experiment_runner.py — validates the actual thesis claim in code
from app.domain.enums import RiskLevel
from app.services.adaptive_scheduler import AdaptiveScheduler
from app.services.experiments.experiment_runner import run_experiment
from app.services.experiments.scenarios import low_risk_scenario, medium_risk_scenario, wildfire_scenario
from app.services.fixed_interval_scheduler import FixedIntervalScheduler
from app.services.risk_assessment.rule_based_risk_assessor import RuleBasedRiskAssessor
from app.services.scheduling_policy import SchedulingPolicy

FIXED = lambda h, td: FixedIntervalScheduler(RuleBasedRiskAssessor(), h, tick_duration_seconds=td)
ADAPTIVE = lambda h, td: AdaptiveScheduler(
    RuleBasedRiskAssessor(),
    SchedulingPolicy({
        RiskLevel.LOW: 600,
        RiskLevel.MEDIUM: 200,
        RiskLevel.HIGH: 60,
        RiskLevel.EMERGENCY: 30
    }),
    h,
    td
)


def test_adaptive_is_more_vigilant_than_fixed_under_sustained_medium_risk():
    config = medium_risk_scenario(node_count=20, duration_ticks=300, seed=1)
    fixed = run_experiment("medium_risk", "fixed", FIXED, **config)
    adaptive = run_experiment("medium_risk", "adaptive", ADAPTIVE, **config)

    assert adaptive.average_interval_seconds < fixed.average_interval_seconds


def test_adaptive_settles_longer_than_fixed_under_low_risk():
    config = low_risk_scenario(node_count=20, duration_ticks=300, seed=2)
    fixed = run_experiment("low_risk", "fixed", FIXED, **config)
    adaptive = run_experiment("low_risk", "adaptive", ADAPTIVE, **config)

    assert adaptive.average_interval_seconds > fixed.average_interval_seconds


def test_wildfire_scenario_measures_detection_latency_when_detected():
    config = wildfire_scenario(node_count=50, duration_ticks=500, seed=3)
    result = run_experiment("wildfire", "adaptive", ADAPTIVE, **config)

    assert config["ignition_tick"] is not None
    if result.first_emergency_tick is not None:
        assert result.detection_latency_ticks >= 0