# tests/test_feature_engineering.py
from app.domain.sensor_reading import SensorReading
from app.services.risk_assessment.feature_engineering import FEATURE_NAMES, extract_features


def test_extract_features_includes_dryness_index():
    features = extract_features(SensorReading(temperature=30, humidity=20, smoke=2.0))
    assert features["dryness_index"] == 10
    assert set(features.keys()) == set(FEATURE_NAMES)