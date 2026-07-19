import numpy as np

from app.domain.environment import EnvironmentState
from app.services.generators.humidity import HumidityGenerator
from app.services.generators.rain import RainGenerator
from app.services.generators.smoke import SmokeGenerator
from app.services.generators.temperature import TemperatureGenerator
from app.services.generators.wind import WindGenerator
from app.services.simulation_clock import SimulationClock


class SimulationEngine:
    """Orchestrates the generators in explicit dependency order:
    temperature -> humidity -> wind -> rain -> smoke. Deliberately not a
    generic pipeline — the ordering *is* the physical model, and hiding
    it behind an abstraction would make the coupling harder to follow,
    not easier."""

    def __init__(
        self,
        clock: SimulationClock,
        temperature_gen: TemperatureGenerator,
        humidity_gen: HumidityGenerator,
        wind_gen: WindGenerator,
        rain_gen: RainGenerator,
        smoke_gen: SmokeGenerator,
    ):
        self._clock = clock
        self._temperature_gen = temperature_gen
        self._humidity_gen = humidity_gen
        self._wind_gen = wind_gen
        self._rain_gen = rain_gen
        self._smoke_gen = smoke_gen
        self._state: EnvironmentState | None = None

    def step(self, fire_risk_multiplier: float = 1.0) -> EnvironmentState:
        tick = self._clock.advance()
        prev = self._state

        temperature = self._temperature_gen.generate(tick)
        humidity = self._humidity_gen.generate(temperature)
        wind_speed = self._wind_gen.generate(prev.wind_speed if prev else 8.0)
        is_raining, rain_intensity = self._rain_gen.generate(prev.is_raining if prev else False)
        smoke = self._smoke_gen.generate(wind_speed, rain_intensity, fire_risk_multiplier)

        self._state = EnvironmentState(
            tick=tick,
            ambient_temperature=temperature,
            ambient_humidity=humidity,
            ambient_smoke=smoke,
            wind_speed=wind_speed,
            is_raining=is_raining,
            rain_intensity=rain_intensity,
        )
        return self._state


def create_default_simulation_engine(seed: int = 42) -> SimulationEngine:
    """Composition root: one seed determines an entire experiment run."""
    rng = np.random.default_rng(seed)
    return SimulationEngine(
        clock=SimulationClock(),
        temperature_gen=TemperatureGenerator(rng=rng),
        humidity_gen=HumidityGenerator(rng=rng),
        wind_gen=WindGenerator(rng=rng),
        rain_gen=RainGenerator(rng=rng),
        smoke_gen=SmokeGenerator(rng=rng),
    )