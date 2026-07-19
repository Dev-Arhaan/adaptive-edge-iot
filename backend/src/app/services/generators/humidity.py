import numpy as np


class HumidityGenerator:
    """Anti-correlated with temperature (hot air holds relative humidity
    down), clamped to a physically valid [0, 100] range."""

    def __init__(
        self,
        base_humidity: float = 55.0,
        temp_coupling: float = -1.4,
        reference_temp: float = 22.0,
        noise_std: float = 1.5,
        rng: np.random.Generator | None = None,
    ):
        self._base = base_humidity
        self._coupling = temp_coupling
        self._reference_temp = reference_temp
        self._noise_std = noise_std
        self._rng = rng or np.random.default_rng()

    def generate(self, temperature: float) -> float:
        delta = self._coupling * (temperature - self._reference_temp)
        noise = self._rng.normal(0, self._noise_std)
        return min(100.0, max(0.0, self._base + delta + noise))