import numpy as np


class SmokeGenerator:
    """Baseline near-zero smoke; grows when a scenario injects fire risk.

    fire_risk_multiplier is the deliberate hook for Phase 8: a future
    ScenarioController ramps this from 1.0 upward to script a wildfire
    event, without SmokeGenerator needing to know what a "wildfire" is.
    """

    def __init__(
        self,
        baseline: float = 0.5,
        wind_spread_factor: float = 0.3,
        rain_suppression_factor: float = 0.6,
        noise_std: float = 0.1,
        rng: np.random.Generator | None = None,
    ):
        self._baseline = baseline
        self._wind_spread_factor = wind_spread_factor
        self._rain_suppression = rain_suppression_factor
        self._noise_std = noise_std
        self._rng = rng or np.random.default_rng()

    def generate(
        self, wind_speed: float, rain_intensity: float, fire_risk_multiplier: float = 1.0
    ) -> float:
        raw = self._baseline * fire_risk_multiplier
        raw += raw * (wind_speed * self._wind_spread_factor / 10)
        raw -= raw * min(1.0, rain_intensity * self._rain_suppression / 10)
        noise = self._rng.normal(0, self._noise_std)
        return max(0.0, raw + noise)