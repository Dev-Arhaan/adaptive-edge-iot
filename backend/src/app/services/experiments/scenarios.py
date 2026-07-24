"""Named scenario builders for Phase 8. Plain functions rather than a
generic Scenario class hierarchy — three scenario types don't need
inheritance, and a runner script reading these directly is easier to
audit for a thesis appendix than one more layer of indirection."""

from app.services.scenarios.constant_risk_injector import ConstantRiskInjector
from app.services.scenarios.fire_episode_injector import FireEpisodeInjector
from app.services.spatial_field import scatter_anchors

DEFAULT_WIDTH = 1000
DEFAULT_HEIGHT = 1000
DEFAULT_ANCHOR_COUNT = 5


def low_risk_scenario(node_count: int = 150, duration_ticks: int = 1440, seed: int = 100) -> dict:
    anchors = scatter_anchors(DEFAULT_ANCHOR_COUNT, DEFAULT_WIDTH, DEFAULT_HEIGHT, seed=seed)
    injector = ConstantRiskInjector([a.id for a in anchors], multiplier=1.0)
    return dict(node_count=node_count, duration_ticks=duration_ticks, seed=seed, injector=injector, ignition_tick=None)


def medium_risk_scenario(
    node_count: int = 150, duration_ticks: int = 1440, seed: int = 200, multiplier: float = 3.0
) -> dict:
    anchors = scatter_anchors(DEFAULT_ANCHOR_COUNT, DEFAULT_WIDTH, DEFAULT_HEIGHT, seed=seed)
    injector = ConstantRiskInjector([a.id for a in anchors], multiplier=multiplier)
    return dict(node_count=node_count, duration_ticks=duration_ticks, seed=seed, injector=injector, ignition_tick=None)


def wildfire_scenario(
    node_count: int = 150, duration_ticks: int = 1440, seed: int = 300, peak_multiplier: float = 25.0
) -> dict:
    anchors = scatter_anchors(DEFAULT_ANCHOR_COUNT, DEFAULT_WIDTH, DEFAULT_HEIGHT, seed=seed)
    injector = FireEpisodeInjector(
        [a.id for a in anchors], episode_length_ticks=duration_ticks, peak_multiplier=peak_multiplier,
        fire_probability=1.0, seed=seed,
    )
    return dict(
        node_count=node_count, duration_ticks=duration_ticks, seed=seed,
        injector=injector, ignition_tick=injector.ignition_tick,
    )


def large_scale_scenario(node_count: int = 600, duration_ticks: int = 1440, seed: int = 400) -> dict:
    return wildfire_scenario(node_count=node_count, duration_ticks=duration_ticks, seed=seed)


def stress_test_scenario(node_count: int = 1200, duration_ticks: int = 2880, seed: int = 500) -> dict:
    """Primarily a performance/robustness check — wall_clock_seconds in
    the result is the number that matters here, including whether
    ClusterManager's O(n^2) setup pass (flagged back in Phase 3) is still
    acceptable at this scale."""
    return wildfire_scenario(node_count=node_count, duration_ticks=duration_ticks, seed=seed)