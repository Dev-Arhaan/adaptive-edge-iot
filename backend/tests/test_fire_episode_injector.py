# tests/test_fire_episode_injector.py
from app.services.scenarios.fire_episode_injector import FireEpisodeInjector
from app.services.spatial_field import scatter_anchors


def test_no_fire_stays_at_baseline():
    anchors = scatter_anchors(3, 100, 100, seed=1)
    injector = FireEpisodeInjector(anchors, episode_length_ticks=100, fire_probability=0.0, seed=1)
    assert all(m == 1.0 for t in range(100) for m in injector.multiplier_at(t).values())


def test_fire_ramps_up_then_back_down():
    anchors = scatter_anchors(3, 100, 100, seed=2)
    injector = FireEpisodeInjector(
        anchors, episode_length_ticks=300, fire_probability=1.0, peak_multiplier=10.0, seed=2
    )
    values = [max(injector.multiplier_at(t).values()) for t in range(300)]
    assert max(values) > 5.0
    assert values[0] == 1.0
    assert values[-1] == 1.0