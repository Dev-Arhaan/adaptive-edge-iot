# tests/test_simulation_session.py
from app.services.simulation_session import SimulationSessionManager


def test_start_initializes_running_forest():
    manager = SimulationSessionManager()
    manager.start(node_count=10, seed=1)
    snapshot = manager.snapshot()
    assert snapshot["started"] is True
    assert snapshot["running"] is True
    assert snapshot["node_count"] == 10


def test_pause_stops_stepping():
    manager = SimulationSessionManager()
    manager.start(node_count=5, seed=2)
    manager.pause()
    manager.step_once()
    assert manager.snapshot()["tick"] == 0


def test_inject_scenario_before_start_raises():
    manager = SimulationSessionManager()
    try:
        manager.inject_scenario("wildfire")
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass