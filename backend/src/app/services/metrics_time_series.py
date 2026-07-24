from dataclasses import dataclass


@dataclass(frozen=True)
class MetricsSnapshot:
    tick: int
    average_interval_seconds: float
    total_wakes: int
    emergency_wakes_since_last: int
    average_battery: float


class MetricsTimeSeries:
    """Rolling, capped buffer of periodic snapshots — what Live charts
    consume. Capped rather than growing forever: a live console session
    could run indefinitely, and nothing downstream needs more than a
    recent window to draw a trend."""

    def __init__(self, max_points: int = 300):
        self._max_points = max_points
        self._points: list[MetricsSnapshot] = []

    def record(self, snapshot: MetricsSnapshot) -> None:
        self._points.append(snapshot)
        if len(self._points) > self._max_points:
            self._points.pop(0)

    def all_points(self) -> list[MetricsSnapshot]:
        return list(self._points)