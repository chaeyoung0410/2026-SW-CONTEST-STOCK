from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Question(Base):
    __tablename__ = "question"

    question_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stage_id: Mapped[int] = mapped_column(ForeignKey("stage.stage_id"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    choice1: Mapped[str] = mapped_column(String(255), nullable=False)
    choice2: Mapped[str] = mapped_column(String(255), nullable=False)
    choice3: Mapped[str] = mapped_column(String(255), nullable=False)
    choice4: Mapped[str] = mapped_column(String(255), nullable=False)
    answer: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    tag: Mapped[str] = mapped_column(String(50), nullable=False)

    stage = relationship("Stage", back_populates="questions")
