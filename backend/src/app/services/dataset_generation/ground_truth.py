from app.domain.enums import RiskLevel

# Thresholds on the *authoritative* injected fire multiplier — a value
# neither the rule engine nor the ML model ever sees directly. This is
# deliberately a different variable from RuleBasedRiskAssessor's
# thresholds (which act on noisy sensed smoke/temperature/humidity):
# ground truth is "how severe is the fire really"; both models have to
# infer that from indirect measurements.
def severity_to_risk_level(multiplier: float) -> RiskLevel:
    if multiplier >= 15.0:
        return RiskLevel.EMERGENCY
    if multiplier >= 5.0:
        return RiskLevel.HIGH
    if multiplier >= 1.5:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW