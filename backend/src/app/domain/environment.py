from dataclasses import dataclass


@dataclass
class EnvironmentState:
    tick: int
    ambient_temperature: float
    ambient_humidity: float
    ambient_smoke: float
    wind_speed: float
    is_raining: bool
    rain_intensity: float