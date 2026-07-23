# tests/test_predictions_api.py (replaces Phase 5's version)
from fastapi.testclient import TestClient
from sklearn.tree import DecisionTreeClassifier
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.model_registry import get_ml_risk_assessor, get_shap_explainer
from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.services.risk_assessment.feature_engineering import FEATURE_NAMES
from app.services.risk_assessment.ml_risk_assessor import MLRiskAssessor
from app.services.risk_assessment.shap_explainer import ShapExplainer


def _toy_model():
    import pandas as pd
    X = pd.DataFrame([[20, 60, 0.2, -40], [40, 10, 20, 30]], columns=FEATURE_NAMES)
    return DecisionTreeClassifier(random_state=0).fit(X, ["low", "emergency"])


def test_predict_then_explain_roundtrip():
    # StaticPool keeps one shared in-memory DB across the two requests below —
    # without it, each dependency-injected session would get its own
    # throwaway :memory: database and "explain" could never find the row.
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def _db_override():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    model = _toy_model()
    app.dependency_overrides[get_ml_risk_assessor] = lambda: MLRiskAssessor(
        model, FEATURE_NAMES, model.classes_.tolist()
    )
    app.dependency_overrides[get_shap_explainer] = lambda: ShapExplainer(
        model, FEATURE_NAMES, model.classes_.tolist()
    )
    app.dependency_overrides[get_db_session] = _db_override
    client = TestClient(app)

    predict_response = client.post("/api/v1/predictions/risk", json={"temperature": 38, "humidity": 15, "smoke": 18})
    assert predict_response.status_code == 200
    prediction_id = predict_response.json()["id"]

    explain_response = client.get(f"/api/v1/predictions/{prediction_id}/explain")
    assert explain_response.status_code == 200
    assert len(explain_response.json()["contributions"]) == len(FEATURE_NAMES)

    app.dependency_overrides.clear()


def test_explain_unknown_prediction_returns_404():
    model = _toy_model()
    app.dependency_overrides[get_shap_explainer] = lambda: ShapExplainer(model, FEATURE_NAMES, model.classes_.tolist())
    client = TestClient(app)

    response = client.get("/api/v1/predictions/999999/explain")
    assert response.status_code == 404

    app.dependency_overrides.clear()