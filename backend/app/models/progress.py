from sqlalchemy import Boolean, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("user_id", "stage_id", name="uq_progress_user_stage"),)

    progress_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), nullable=False)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stage.stage_id"), nullable=False)
    cleared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    user = relationship("User", back_populates="progress")
    stage = relationship("Stage", back_populates="progress")
