import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from app.domain.enums import RiskLevel
from app.domain.risk_assessment import RiskAssessment
from app.domain.sensor_reading import SensorReading
from app.services.risk_assessment.feature_engineering import extract_features


class MLRiskAssessor:
    """Second implementation of Phase 4's RiskAssessor protocol —
    AdaptiveScheduler needed zero changes to accept this. Unlike
    RuleBasedRiskAssessor, this reports a genuine confidence score:
    a decision tree naturally produces class probabilities where
    hardcoded rules only produce a boolean match."""

    def __init__(self, model: DecisionTreeClassifier, feature_names: list[str], label_classes: list[str]):
        self._model = model
        self._feature_names = feature_names
        self._label_classes = label_classes

    def assess(self, reading: SensorReading) -> RiskAssessment:
        features = extract_features(reading)
        vector = pd.DataFrame(
            [[features[name] for name in self._feature_names]],
            columns=self._feature_names
        )
        probabilities = self._model.predict_proba(vector)[0]
        best_index = int(np.argmax(probabilities))

        return RiskAssessment(
            level=RiskLevel(self._label_classes[best_index]),
            reason="ml_decision_tree_prediction",
            confidence=float(probabilities[best_index]),
        )