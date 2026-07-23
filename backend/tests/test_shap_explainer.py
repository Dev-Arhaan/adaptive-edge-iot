# tests/test_shap_explainer.py
from sklearn.tree import DecisionTreeClassifier

from app.domain.sensor_reading import SensorReading
from app.services.risk_assessment.feature_engineering import FEATURE_NAMES
from app.services.risk_assessment.shap_explainer import ShapExplainer


def _toy_model():
    import pandas as pd
    X = pd.DataFrame(
        [[20, 60, 0.2, -40], [22, 55, 0.3, -33], [35, 20, 6, 15], [38, 15, 20, 23], [40, 10, 22, 30]],
        columns=FEATURE_NAMES
    )
    y = ["low", "low", "high", "high", "emergency"]
    return DecisionTreeClassifier(max_depth=4, random_state=0).fit(X, y)


def test_explain_returns_one_contribution_per_feature():
    model = _toy_model()
    explainer = ShapExplainer(model, FEATURE_NAMES, model.classes_.tolist())

    explanation = explainer.explain(SensorReading(temperature=39, humidity=12, smoke=21))

    assert {c.feature_name for c in explanation.contributions} == set(FEATURE_NAMES)
    magnitudes = [abs(c.shap_value) for c in explanation.contributions]
    assert magnitudes == sorted(magnitudes, reverse=True)