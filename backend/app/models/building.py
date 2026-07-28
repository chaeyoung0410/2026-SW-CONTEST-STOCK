from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Building(Base):
    __tablename__ = "building"

    building_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), unique=True, nullable=False)
    image: Mapped[str] = mapped_column(String(255), nullable=False)

    user = relationship("User", back_populates="building")
