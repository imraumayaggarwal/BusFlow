from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )

    student_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    course: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    branch: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    destination_id: Mapped[int] = mapped_column(
        ForeignKey("routes.route_id"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="student"
    )

    destination_route = relationship(
        "Route",
        back_populates="students"
    )