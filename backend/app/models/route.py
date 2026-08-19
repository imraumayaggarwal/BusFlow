from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Route(Base):
    __tablename__ = "routes"

    route_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    start_location: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    end_location: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    students = relationship(
        "Student",
        back_populates="destination_route"
    )

    assignments = relationship(
        "BusAssignment",
        back_populates="route",
        cascade="all, delete-orphan"
    )

    departure_statistics = relationship(
        "DepartureStatistic",
        back_populates="route"
    )