import numpy as np
import pandas as pd
import shap
from sklearn.tree import DecisionTreeClassifier

from app.domain.enums import RiskLevel
from app.domain.explanation import Explanation, FeatureContribution
from app.domain.sensor_reading import SensorReading
from app.services.risk_assessment.feature_engineering import extract_features


class ShapExplainer:
    """Wraps shap.TreeExplainer for exact, per-prediction explanations.
    Deliberately a separate service from MLRiskAssessor and never called
    from the hot prediction path — SHAP is comparatively expensive, and
    "explain everything automatically" is not what a dashboard user
    actually wants. Invoked only via the explain API, on demand.
    """

    def __init__(self, model: DecisionTreeClassifier, feature_names: list[str], label_classes: list[str]):
        self._model = model
        self._explainer = shap.TreeExplainer(model)
        self._feature_names = feature_names
        self._label_classes = label_classes

    def explain(self, reading: SensorReading) -> Explanation:
        features = extract_features(reading)
        vector = pd.DataFrame(
            [[features[name] for name in self._feature_names]],
            columns=self._feature_names
        )

        probabilities = self._model.predict_proba(vector)[0]
        predicted_index = int(np.argmax(probabilities))

        shap_output = self._explainer(vector)
        values = shap_output.values[0]
        base_values = shap_output.base_values[0]

        # SHAP's output shape for multiclass trees has varied across
        # versions: (n_features, n_classes) is the common case, but some
        # versions collapse to (n_features,). Handle both defensively —
        # worth a quick sanity check against your installed `shap` version.
        if values.ndim == 2:
            class_values = values[:, predicted_index]
            base_value = float(np.ravel(base_values)[predicted_index])
        else:
            class_values = values
            base_value = float(np.ravel(base_values)[0])

        contributions = sorted(
            (
                FeatureContribution(feature_name=name, value=features[name], shap_value=float(sv))
                for name, sv in zip(self._feature_names, class_values)
            ),
            key=lambda c: abs(c.shap_value),
            reverse=True,
        )

        return Explanation(
            predicted_level=RiskLevel(self._label_classes[predicted_index]),
            confidence=float(probabilities[predicted_index]),
            base_value=base_value,
            contributions=contributions,
        )