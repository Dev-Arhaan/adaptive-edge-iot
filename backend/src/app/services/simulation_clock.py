class SimulationClock:
    """Virtual time source. Every other service reads 'now' from here,
    never from datetime.now() — experiments must run faster than real
    time and be exactly reproducible given a seed."""

    def __init__(self, tick_duration_seconds: int = 60, start_tick: int = 0):
        self._tick_duration_seconds = tick_duration_seconds
        self._tick = start_tick

    @property
    def tick(self) -> int:
        return self._tick

    @property
    def elapsed_seconds(self) -> int:
        return self._tick * self._tick_duration_seconds

    def advance(self, steps: int = 1) -> int:
        self._tick += steps
        return self._tick