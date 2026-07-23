from functools import lru_cache

import joblib

from app.core.config import settings
from app.services.risk_assessment.ml_risk_assessor import MLRiskAssessor
from app.services.risk_assessment.shap_explainer import ShapExplainer


@lru_cache
def _load_model_bundle() -> dict:
    return joblib.load(settings.model_artifact_path)


@lru_cache
def get_ml_risk_assessor() -> MLRiskAssessor:
    bundle = _load_model_bundle()
    return MLRiskAssessor(
        model=bundle["model"], feature_names=bundle["feature_names"], label_classes=bundle["label_classes"]
    )


@lru_cache
def get_shap_explainer() -> ShapExplainer:
    bundle = _load_model_bundle()
    return ShapExplainer(
        model=bundle["model"], feature_names=bundle["feature_names"], label_classes=bundle["label_classes"]
    )


@lru_cache
def get_feature_importance() -> dict[str, float]:
    return _load_model_bundle().get("feature_importance", {})