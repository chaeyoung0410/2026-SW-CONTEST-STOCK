from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AnswerAttempt(Base):
    """문제 단위 풀이 기록.

    submission_id가 있는 요청은 사용자별로 한 번만 저장해 네트워크 재전송이나
    더블 클릭으로 동일 답안이 중복 집계되는 것을 막는다. 기존 클라이언트처럼
    submission_id가 없는 요청은 각각 별도 풀이 시도로 기록한다.
    """

    __tablename__ = "answer_attempt"
    __table_args__ = (
        UniqueConstraint("user_id", "submission_id", name="uq_answer_attempt_user_submission"),
        CheckConstraint(
            "selected_answer IS NULL OR selected_answer BETWEEN 1 AND 4",
            name="ck_answer_attempt_selected_answer",
        ),
        Index("ix_answer_attempt_user_stage_created", "user_id", "stage_id", "created_at"),
    )

    attempt_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), nullable=False)
    question_id: Mapped[int | None] = mapped_column(ForeignKey("question.question_id"), nullable=True)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stage.stage_id"), nullable=False)
    result_id: Mapped[int | None] = mapped_column(
        ForeignKey("result.result_id"), nullable=True, index=True
    )
    selected_answer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    submission_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = relationship("User", back_populates="answer_attempts")
    question = relationship("Question")
    stage = relationship("Stage", back_populates="answer_attempts")
    result = relationship("Result", back_populates="answer_attempts")
