from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Result(Base):
    __tablename__ = "result"
    __table_args__ = (
        UniqueConstraint("user_id", "submission_id", name="uq_result_user_submission"),
        CheckConstraint("score >= 0", name="ck_result_score_nonnegative"),
        CheckConstraint("correct_count >= 0", name="ck_result_correct_nonnegative"),
        CheckConstraint("total_question > 0", name="ck_result_total_positive"),
        CheckConstraint("correct_count <= total_question", name="ck_result_correct_not_over_total"),
    )

    result_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stage.stage_id"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_question: Mapped[int] = mapped_column(Integer, nullable=False)
    submission_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = relationship("User", back_populates="results")
    stage = relationship("Stage", back_populates="results")
    answer_attempts = relationship("AnswerAttempt", back_populates="result")
