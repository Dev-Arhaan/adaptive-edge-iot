from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PredictionLogModel(Base):
    """Deliberately scoped to ML prediction requests only — not a
    general-purpose event log. Persisting scheduling decisions or node
    telemetry is real, separate work for whatever Phase 7's dashboard
    actually ends up querying."""

    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    temperature: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    smoke: Mapped[float] = mapped_column(Float)
    dryness_index: Mapped[float] = mapped_column(Float)
    predicted_level: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))