# tests/test_simulation_engine.py
from app.services.simulation_engine import create_default_simulation_engine


def test_engine_run_is_fully_reproducible_given_seed():
    run_a = [create_default_simulation_engine(seed=7).step() for _ in range(50)]
    run_b = [create_default_simulation_engine(seed=7).step() for _ in range(50)]
    assert run_a == run_b