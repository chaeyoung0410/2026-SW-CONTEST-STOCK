from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Stage(Base):
    __tablename__ = "stage"

    stage_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)

    learning_contents = relationship("Learning", back_populates="stage")
    questions = relationship("Question", back_populates="stage")
    progress = relationship("Progress", back_populates="stage")
    results = relationship("Result", back_populates="stage")
    histories = relationship("History", back_populates="stage")
