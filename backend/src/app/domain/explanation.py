from dataclasses import dataclass

from app.domain.enums import RiskLevel


@dataclass(frozen=True)
class FeatureContribution:
    feature_name: str
    value: float
    shap_value: float


@dataclass(frozen=True)
class Explanation:
    predicted_level: RiskLevel
    confidence: float
    base_value: float
    contributions: list[FeatureContribution]  # sorted by |shap_value| descending