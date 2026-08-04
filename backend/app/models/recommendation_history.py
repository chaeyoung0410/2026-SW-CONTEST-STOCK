from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"
    __table_args__ = (
        CheckConstraint("priority >= 1", name="ck_recommendation_priority_positive"),
        CheckConstraint("recommendation_score >= 0", name="ck_recommendation_score_nonnegative"),
        Index("ix_recommendation_user_stage_time", "user_id", "stage_id", "recommended_at"),
    )

    recommendation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stage.stage_id"), nullable=False)
    learning_id: Mapped[int | None] = mapped_column(ForeignKey("learning.learning_id"), nullable=True)
    recommended_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation_score: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    clicked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    learning_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="recommendation_history")
    stage = relationship("Stage", back_populates="recommendation_history")
    learning = relationship("Learning")
