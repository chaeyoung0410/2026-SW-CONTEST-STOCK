from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RemedialQuestionCache(Base):
    """사용자와 원본 문제별 Gemini 생성 결과 및 재시도 상태."""

    __tablename__ = "remedial_question_cache"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "source_question_id",
            name="uq_remedial_cache_user_question",
        ),
        CheckConstraint(
            "status IN ('pending', 'ready', 'unavailable')",
            name="ck_remedial_cache_status",
        ),
        Index("ix_remedial_cache_user_question", "user_id", "source_question_id"),
    )

    cache_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), nullable=False)
    source_question_id: Mapped[int] = mapped_column(
        ForeignKey("question.question_id"), nullable=False
    )
    stage_id: Mapped[int] = mapped_column(ForeignKey("stage.stage_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    retry_after: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
