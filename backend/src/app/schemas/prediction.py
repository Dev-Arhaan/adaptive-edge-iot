from pydantic import BaseModel, Field


class SensorReadingRequest(BaseModel):
    temperature: float
    humidity: float = Field(..., ge=0, le=100)
    smoke: float = Field(..., ge=0)


class RiskPredictionResponse(BaseModel):
    id: int
    level: str
    confidence: float
    reason: str


class FeatureContributionSchema(BaseModel):
    feature_name: str
    value: float
    shap_value: float


class ExplanationResponse(BaseModel):
    prediction_id: int
    predicted_level: str
    confidence: float
    base_value: float
    contributions: list[FeatureContributionSchema]


class FeatureImportanceResponse(BaseModel):
    importances: dict[str, float]