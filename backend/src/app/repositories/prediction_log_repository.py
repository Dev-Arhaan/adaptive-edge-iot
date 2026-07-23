from sqlalchemy.orm import Session

from app.models.prediction_log import PredictionLogModel


class PredictionLogRepository:
    """Only layer that knows about SQLAlchemy for prediction logs — the
    API layer and domain code stay free of session/ORM details."""

    def __init__(self, session: Session):
        self._session = session

    def save(
        self,
        *,
        temperature: float,
        humidity: float,
        smoke: float,
        dryness_index: float,
        predicted_level: str,
        confidence: float,
        reason: str,
    ) -> PredictionLogModel:
        row = PredictionLogModel(
            temperature=temperature,
            humidity=humidity,
            smoke=smoke,
            dryness_index=dryness_index,
            predicted_level=predicted_level,
            confidence=confidence,
            reason=reason,
        )
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return row

    def get_by_id(self, prediction_id: int) -> PredictionLogModel | None:
        return self._session.get(PredictionLogModel, prediction_id)