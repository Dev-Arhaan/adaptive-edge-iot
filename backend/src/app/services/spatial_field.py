import math
from dataclasses import dataclass

import numpy as np

from app.domain.environment import EnvironmentState
from app.domain.spatial_anchor import SpatialAnchor
from app.services.generators.humidity import HumidityGenerator
from app.services.generators.rain import RainGenerator
from app.services.generators.smoke import SmokeGenerator
from app.services.generators.temperature import TemperatureGenerator
from app.services.generators.wind import WindGenerator
from app.services.simulation_clock import SimulationClock
from app.services.simulation_engine import SimulationEngine

_EPSILON = 1e-6  # avoids divide-by-zero when a query point sits on an anchor


@dataclass
class _AnchorRuntime:
    anchor: SpatialAnchor
    engine: SimulationEngine
    last_state: EnvironmentState | None = None


class SpatialField:
    """Owns N independent SimulationEngine instances, one per SpatialAnchor,
    and answers environment queries at any (x, y) via inverse-distance-
    weighted interpolation across them.

    Deliberate first-order spatial model: gives correlated, smoothly-varying
    conditions and lets localized fire risk "reach" nearby nodes, without a
    full physical spread model (wind-directional spread, terrain, fuel load
    are explicitly out of scope — a limitation to name, not hide).
    """

    def __init__(self, anchors: list[_AnchorRuntime], idw_power: float = 2.0):
        if not anchors:
            raise ValueError("SpatialField requires at least one anchor")
        self._anchors = anchors
        self._idw_power = idw_power

    def step(self, fire_risk_by_anchor: dict[str, float] | None = None) -> None:
        """Advance every anchor by one tick. fire_risk_by_anchor lets a
        future Phase 8 ScenarioController inject risk at specific anchors
        (a fire origin) without SpatialField needing to know what a
        "wildfire" is."""
        fire_risk_by_anchor = fire_risk_by_anchor or {}
        for runtime in self._anchors:
            multiplier = fire_risk_by_anchor.get(runtime.anchor.id, 1.0)
            runtime.last_state = runtime.engine.step(fire_risk_multiplier=multiplier)

    def anchor_state(self, anchor_id: str) -> EnvironmentState:
        for runtime in self._anchors:
            if runtime.anchor.id == anchor_id:
                if runtime.last_state is None:
                    raise RuntimeError("SpatialField.step() must be called before sampling")
                return runtime.last_state
        raise KeyError(anchor_id)

    def interpolate_scalar(self, x: float, y: float, values_by_anchor: dict[str, float]) -> float:
        """Generic IDW interpolation over any per-anchor scalar. sample_at
        uses this for EnvironmentState fields; dataset generation reuses
        it directly on FireEpisodeInjector's multiplier dict to compute
        ground-truth severity at any point — a value sample_at's
        EnvironmentState blend never touches."""
        weights, values = [], []
        for runtime in self._anchors:
            distance = math.hypot(x - runtime.anchor.x, y - runtime.anchor.y)
            anchor_value = values_by_anchor[runtime.anchor.id]
            if distance < _EPSILON:
                return anchor_value
            weights.append(1.0 / (distance**self._idw_power))
            values.append(anchor_value)
        total_weight = sum(weights)
        return sum(w * v for w, v in zip(weights, values)) / total_weight

    def sample_at(self, x: float, y: float) -> EnvironmentState:
        if any(runtime.last_state is None for runtime in self._anchors):
            raise RuntimeError("SpatialField.step() must be called before sampling")

        def blend(field: str) -> float:
            values_by_anchor = {rt.anchor.id: getattr(rt.last_state, field) for rt in self._anchors}
            return self.interpolate_scalar(x, y, values_by_anchor)

        rain_intensity = blend("rain_intensity")
        return EnvironmentState(
            tick=self._anchors[0].last_state.tick,
            ambient_temperature=blend("ambient_temperature"),
            ambient_humidity=blend("ambient_humidity"),
            ambient_smoke=blend("ambient_smoke"),
            wind_speed=blend("wind_speed"),
            is_raining=rain_intensity > 0.1,
            rain_intensity=rain_intensity,
        )


def scatter_anchors(count: int, width: float, height: float, seed: int = 42) -> list[SpatialAnchor]:
    """Deterministically scatters N anchors uniformly over a width x height
    area. Anchor density is a simulation parameter you'll want to justify
    experimentally (too sparse = blocky transitions between nodes)."""
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0, width, size=count)
    ys = rng.uniform(0, height, size=count)
    return [SpatialAnchor(id=f"anchor-{i}", x=float(x), y=float(y)) for i, (x, y) in enumerate(zip(xs, ys))]


def create_default_spatial_field(
    anchors: list[SpatialAnchor], seed: int = 42, idw_power: float = 2.0
) -> SpatialField:
    """Composition root for the spatial layer. Spawns one independent,
    reproducible child RNG per anchor from a single seed, so the whole
    field is deterministic run-to-run while anchors stay uncorrelated."""
    child_rngs = np.random.default_rng(seed).spawn(len(anchors))

    runtimes = [
        _AnchorRuntime(
            anchor=anchor,
            engine=SimulationEngine(
                clock=SimulationClock(),
                temperature_gen=TemperatureGenerator(rng=rng),
                humidity_gen=HumidityGenerator(rng=rng),
                wind_gen=WindGenerator(rng=rng),
                rain_gen=RainGenerator(rng=rng),
                smoke_gen=SmokeGenerator(rng=rng),
            ),
        )
        for anchor, rng in zip(anchors, child_rngs)
    ]
    return SpatialField(runtimes, idw_power=idw_power)