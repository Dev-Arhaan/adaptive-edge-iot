from app.domain.spatial_anchor import SpatialAnchor


class ConstantRiskInjector:
    """Models ambient, weather-driven risk elevation — every anchor held
    at the same constant multiplier for the whole run. Distinct from
    FireEpisodeInjector on purpose: this represents a sustained dry/windy
    period, not a discrete, localized fire event. Used for the low-risk
    (multiplier=1.0) and medium-risk (multiplier>1.0) baseline scenarios.
    """

    def __init__(self, anchors: list[SpatialAnchor], multiplier: float):
        self._anchor_ids = [a.id for a in anchors]
        self._multiplier = multiplier

    def multiplier_at(self, tick: int) -> dict[str, float]:
        return {anchor_id: self._multiplier for anchor_id in self._anchor_ids}