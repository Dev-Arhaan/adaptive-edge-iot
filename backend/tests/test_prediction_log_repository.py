# tests/test_prediction_log_repository.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.repositories.prediction_log_repository import PredictionLogRepository


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_save_and_get_by_id_roundtrip():
    repo = PredictionLogRepository(_session())
    saved = repo.save(
        temperature=30, humidity=20, smoke=5, dryness_index=10,
        predicted_level="high", confidence=0.87, reason="ml_decision_tree_prediction",
    )
    assert repo.get_by_id(saved.id).predicted_level == "high"


def test_get_by_id_returns_none_when_missing():
    assert PredictionLogRepository(_session()).get_by_id(999) is None