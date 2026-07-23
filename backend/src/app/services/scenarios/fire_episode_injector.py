import numpy as np

from app.domain.spatial_anchor import SpatialAnchor


class FireEpisodeInjector:
    """Scripts one fire event's lifecycle (baseline -> ramp up -> peak ->
    ramp down -> baseline) at a single randomly chosen anchor across an
    episode. A minimal, scoped-down preview of Phase 8's full
    ScenarioController, built only to generate ground-truth training
    labels — not an attempt at the final experiment framework.
    """

    def __init__(
        self,
        anchors: list[SpatialAnchor],
        episode_length_ticks: int,
        peak_multiplier: float = 25.0,
        fire_probability: float = 0.6,
        seed: int = 0,
    ):
        rng = np.random.default_rng(seed)
        self._anchor_ids = [a.id for a in anchors]
        self._peak_multiplier = peak_multiplier
        self._has_fire = rng.random() < fire_probability

        if self._has_fire:
            self._origin_anchor_id = rng.choice(self._anchor_ids)
            ramp_span = episode_length_ticks // 3
            self._ignition_tick = int(rng.integers(0, max(1, episode_length_ticks - ramp_span)))
            self._ramp_up_ticks = max(1, ramp_span // 2)
            self._hold_ticks = max(1, ramp_span // 4)
            self._ramp_down_ticks = max(1, ramp_span - self._ramp_up_ticks - self._hold_ticks)

    def multiplier_at(self, tick: int) -> dict[str, float]:
        """Per-anchor fire_risk_multiplier for this tick — feed directly
        into SpatialField.step(fire_risk_by_anchor=...) and reuse for
        ground-truth labeling via SpatialField.interpolate_scalar."""
        baseline = {anchor_id: 1.0 for anchor_id in self._anchor_ids}
        if not self._has_fire:
            return baseline

        elapsed = tick - self._ignition_tick
        if elapsed < 0:
            return baseline
        if elapsed < self._ramp_up_ticks:
            current = 1.0 + (elapsed / self._ramp_up_ticks) * (self._peak_multiplier - 1.0)
        elif elapsed < self._ramp_up_ticks + self._hold_ticks:
            current = self._peak_multiplier
        elif elapsed < self._ramp_up_ticks + self._hold_ticks + self._ramp_down_ticks:
            progress = (elapsed - self._ramp_up_ticks - self._hold_ticks) / self._ramp_down_ticks
            current = self._peak_multiplier - progress * (self._peak_multiplier - 1.0)
        else:
            current = 1.0

        baseline[self._origin_anchor_id] = current
        return baseline
    
    @property
    def ignition_tick(self) -> int | None:
        """Exposed so experiment code can compute detection latency
        relative to when the fire actually started. None if this episode
        has no fire at all."""
        return self._ignition_tick if self._has_fire else None