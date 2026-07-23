# tests/test_ml_risk_assessor.py
from sklearn.tree import DecisionTreeClassifier

from app.domain.enums import RiskLevel
from app.domain.sensor_reading import SensorReading
from app.services.risk_assessment.feature_engineering import FEATURE_NAMES
from app.services.risk_assessment.ml_risk_assessor import MLRiskAssessor


def test_assess_returns_valid_level_and_confidence():
    import pandas as pd
    X = pd.DataFrame([[20, 60, 0.2, -40], [40, 10, 20, 30]], columns=FEATURE_NAMES)
    model = DecisionTreeClassifier(random_state=0).fit(X, ["low", "emergency"])
    assessor = MLRiskAssessor(model, FEATURE_NAMES, model.classes_.tolist())

    result = assessor.assess(SensorReading(temperature=38, humidity=15, smoke=18))

    assert isinstance(result.level, RiskLevel)
    assert 0.0 <= result.confidence <= 1.0