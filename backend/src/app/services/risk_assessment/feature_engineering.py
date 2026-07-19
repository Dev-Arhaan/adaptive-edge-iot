from app.domain.sensor_reading import SensorReading

FEATURE_NAMES = ["temperature", "humidity", "smoke", "dryness_index"]


def extract_features(reading: SensorReading) -> dict[str, float]:
    """Single source of truth for feature engineering — imported by both
    the dataset-generation script (training) and MLRiskAssessor
    (inference). There is exactly one implementation, so training-serving
    skew can't creep in the way it would across a notebook and a service
    that each reimplement this.

    dryness_index is the one engineered feature: trees model raw feature
    interactions natively, so heavier engineering has diminishing returns
    here. This one earns its place as a simple, interpretable fire-weather
    heuristic and gives Phase 6's SHAP explainer something concrete.

    wind_speed / rain_intensity are deliberately not separate inputs —
    Phase 2's SmokeGenerator already factors both into `smoke`.
    """
    return {
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "smoke": reading.smoke,
        "dryness_index": reading.temperature - reading.humidity,
    }