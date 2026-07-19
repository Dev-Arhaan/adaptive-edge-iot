# tests/test_simulation_clock.py
from app.services.simulation_clock import SimulationClock


def test_clock_advances_by_default_step():
    clock = SimulationClock(tick_duration_seconds=60)
    assert clock.tick == 0
    clock.advance()
    assert clock.tick == 1
    assert clock.elapsed_seconds == 60


def test_clock_advances_by_custom_steps():
    clock = SimulationClock()
    clock.advance(steps=10)
    assert clock.tick == 10