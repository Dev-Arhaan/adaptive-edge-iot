from dataclasses import dataclass


@dataclass(frozen=True)
class SensorReading:
    """A node's actual sensed values at the moment it wakes — the only
    information a real device would have. Decoupled from Node so Phase 5's
    ML risk assessor can consume the exact same shape without depending on
    the full domain entity."""

    temperature: float
    humidity: float
    smoke: float