# tests/test_constant_risk_injector.py
from app.services.scenarios.constant_risk_injector import ConstantRiskInjector
from app.services.spatial_field import scatter_anchors


def test_multiplier_is_constant_across_ticks():
    anchors = scatter_anchors(3, 100, 100, seed=1)
    injector = ConstantRiskInjector([a.id for a in anchors], multiplier=3.0)
    assert injector.multiplier_at(0) == injector.multiplier_at(500)
    assert all(v == 3.0 for v in injector.multiplier_at(0).values())