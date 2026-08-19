from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Manager(Base):
    __tablename__ = "managers"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )

    manager_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="manager"
    )