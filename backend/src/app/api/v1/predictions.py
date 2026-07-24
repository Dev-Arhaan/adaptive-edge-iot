from app.core.auth import require_auth
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.model_registry import get_feature_importance, get_ml_risk_assessor, get_shap_explainer
from app.db.session import get_db_session
from app.domain.sensor_reading import SensorReading
from app.repositories.prediction_log_repository import PredictionLogRepository
from app.schemas.prediction import (
    ExplanationResponse,
    FeatureContributionSchema,
    FeatureImportanceResponse,
    RiskPredictionResponse,
    SensorReadingRequest,
)
from app.services.risk_assessment.feature_engineering import extract_features
from app.services.risk_assessment.ml_risk_assessor import MLRiskAssessor
from app.services.risk_assessment.shap_explainer import ShapExplainer

router = APIRouter(prefix="/predictions", tags=["predictions"], dependencies=[Depends(require_auth)])

@router.post("/risk", response_model=RiskPredictionResponse)
def predict_risk(
    payload: SensorReadingRequest,
    assessor: MLRiskAssessor = Depends(get_ml_risk_assessor),
    session: Session = Depends(get_db_session),
) -> RiskPredictionResponse:
    reading = SensorReading(temperature=payload.temperature, humidity=payload.humidity, smoke=payload.smoke)
    assessment = assessor.assess(reading)
    features = extract_features(reading)

    log_row = PredictionLogRepository(session).save(
        temperature=features["temperature"],
        humidity=features["humidity"],
        smoke=features["smoke"],
        dryness_index=features["dryness_index"],
        predicted_level=assessment.level.value,
        confidence=assessment.confidence,
        reason=assessment.reason,
    )

    return RiskPredictionResponse(
        id=log_row.id, level=assessment.level.value, confidence=assessment.confidence, reason=assessment.reason
    )


@router.get("/{prediction_id}/explain", response_model=ExplanationResponse)
def explain_prediction(
    prediction_id: int,
    explainer: ShapExplainer = Depends(get_shap_explainer),
    session: Session = Depends(get_db_session),
) -> ExplanationResponse:
    log_row = PredictionLogRepository(session).get_by_id(prediction_id)
    if log_row is None:
        raise HTTPException(status_code=404, detail="Prediction not found")

    reading = SensorReading(temperature=log_row.temperature, humidity=log_row.humidity, smoke=log_row.smoke)
    explanation = explainer.explain(reading)

    return ExplanationResponse(
        prediction_id=prediction_id,
        predicted_level=explanation.predicted_level.value,
        confidence=explanation.confidence,
        base_value=explanation.base_value,
        contributions=[
            FeatureContributionSchema(feature_name=c.feature_name, value=c.value, shap_value=c.shap_value)
            for c in explanation.contributions
        ],
    )


@router.get("/feature-importance", response_model=FeatureImportanceResponse)
def feature_importance(
    importances: dict[str, float] = Depends(get_feature_importance),
) -> FeatureImportanceResponse:
    return FeatureImportanceResponse(importances=importances)