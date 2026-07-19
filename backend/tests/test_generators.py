# tests/test_generators.py
import numpy as np

from app.services.generators.smoke import SmokeGenerator
from app.services.generators.temperature import TemperatureGenerator


def test_temperature_generator_is_deterministic_given_seed():
    seq_a = [TemperatureGenerator(rng=np.random.default_rng(42)).generate(t) for t in range(50)]
    seq_b = [TemperatureGenerator(rng=np.random.default_rng(42)).generate(t) for t in range(50)]
    assert seq_a == seq_b


def test_smoke_rises_with_fire_risk_multiplier():
    gen = SmokeGenerator(rng=np.random.default_rng(1))
    low = gen.generate(wind_speed=5, rain_intensity=0, fire_risk_multiplier=1.0)
    high = gen.generate(wind_speed=5, rain_intensity=0, fire_risk_multiplier=20.0)
    assert high > low