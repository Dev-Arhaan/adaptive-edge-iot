import math

import numpy as np


class TemperatureGenerator:
    """Diurnal cycle (sinusoidal) + Gaussian noise, in Celsius. Independent
    of every other signal — everything else couples off of this."""

    def __init__(
        self,
        base_temp: float = 22.0,
        amplitude: float = 6.0,
        ticks_per_day: int = 1440,
        noise_std: float = 0.3,
        rng: np.random.Generator | None = None,
    ):
        self._base_temp = base_temp
        self._amplitude = amplitude
        self._ticks_per_day = ticks_per_day
        self._noise_std = noise_std
        self._rng = rng or np.random.default_rng()

    def generate(self, tick: int) -> float:
        phase = 2 * math.pi * (tick % self._ticks_per_day) / self._ticks_per_day
        diurnal = self._base_temp + self._amplitude * math.sin(phase - math.pi / 2)
        noise = self._rng.normal(0, self._noise_std)
        return diurnal + noise