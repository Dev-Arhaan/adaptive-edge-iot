import numpy as np


class RainGenerator:
    """Two-state Markov process: rain tends to persist once it starts and
    is rare to begin with. Independent per-tick coin flips would make
    rain flicker on/off every minute, which isn't physically plausible."""

    def __init__(
        self,
        start_prob: float = 0.001,
        continue_prob: float = 0.97,
        max_intensity: float = 10.0,
        rng: np.random.Generator | None = None,
    ):
        self._start_prob = start_prob
        self._continue_prob = continue_prob
        self._max_intensity = max_intensity
        self._rng = rng or np.random.default_rng()

    def generate(self, was_raining: bool) -> tuple[bool, float]:
        is_raining = self._rng.random() < (
            self._continue_prob if was_raining else self._start_prob
        )
        intensity = self._rng.uniform(0.5, self._max_intensity) if is_raining else 0.0
        return is_raining, intensity