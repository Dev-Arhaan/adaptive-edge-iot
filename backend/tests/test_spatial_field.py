# tests/test_spatial_field.py
from app.domain.spatial_anchor import SpatialAnchor
from app.services.spatial_field import create_default_spatial_field, scatter_anchors


def test_sample_at_anchor_position_returns_that_anchors_state():
    anchors = [SpatialAnchor(id="a", x=0, y=0), SpatialAnchor(id="b", x=100, y=100)]
    field = create_default_spatial_field(anchors, seed=1)
    field.step()
    assert field.sample_at(0, 0) == field.anchor_state("a")


def test_closer_anchor_dominates_interpolation():
    anchors = [SpatialAnchor(id="hot", x=0, y=0), SpatialAnchor(id="cold", x=100, y=0)]
    field = create_default_spatial_field(anchors, seed=2)
    field.step()

    hot_temp = field.anchor_state("hot").ambient_temperature
    cold_temp = field.anchor_state("cold").ambient_temperature
    near_hot = field.sample_at(5, 0).ambient_temperature

    assert abs(near_hot - hot_temp) < abs(near_hot - cold_temp)


def test_field_is_reproducible_given_seed():
    anchors = scatter_anchors(count=5, width=500, height=500, seed=10)
    field_a = create_default_spatial_field(anchors, seed=99)
    field_b = create_default_spatial_field(anchors, seed=99)
    field_a.step()
    field_b.step()
    assert field_a.sample_at(123, 45) == field_b.sample_at(123, 45)


def test_sample_before_step_raises():
    anchors = [SpatialAnchor(id="a", x=0, y=0)]
    field = create_default_spatial_field(anchors, seed=3)
    try:
        field.sample_at(0, 0)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass