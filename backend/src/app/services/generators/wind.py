import numpy as np


class WindGenerator:
    """Mean-reverting (Ornstein-Uhlenbeck) process — wind gusts and
    settles, it doesn't follow a diurnal cycle like temperature."""

    def __init__(
        self,
        mean_speed: float = 8.0,
        reversion_rate: float = 0.15,
        volatility: float = 1.2,
        rng: np.random.Generator | None = None,
    ):
        self._mean = mean_speed
        self._theta = reversion_rate
        self._sigma = volatility
        self._rng = rng or np.random.default_rng()

    def generate(self, previous_wind_speed: float) -> float:
        drift = self._theta * (self._mean - previous_wind_speed)
        shock = self._rng.normal(0, self._sigma)
        return max(0.0, previous_wind_speed + drift + shock)