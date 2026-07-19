from dataclasses import dataclass

from app.domain.enums import RiskLevel


@dataclass(frozen=True)
class RiskAssessment:
    """level + reason make the rule engine explainable by construction —
    reason names which rule fired. Phase 6's SHAP explainer for the ML
    path produces a richer but analogous structure, giving a direct
    rule-based-vs-ML-explained comparison for the thesis."""

    level: RiskLevel
    reason: str
    confidence: float = 1.0  # rule-based: deterministic, always certain given its own logic.
                              # ML: actual predict_proba for the winning class.