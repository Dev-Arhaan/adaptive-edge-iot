# tests/test_metrics_time_series.py
from app.services.metrics_time_series import MetricsSnapshot, MetricsTimeSeries


def test_rolling_buffer_caps_at_max_points():
    series = MetricsTimeSeries(max_points=3)
    for tick in range(5):
        series.record(MetricsSnapshot(tick=tick, average_interval_seconds=300, total_wakes=tick, emergency_wakes_since_last=0, average_battery=90))
    points = series.all_points()
    assert len(points) == 3
    assert points[0].tick == 2  # two oldest dropped