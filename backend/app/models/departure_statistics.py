from datetime import date, time

from sqlalchemy import (
    Integer,
    Date,
    Time,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DepartureStatistic(Base):
    __tablename__ = "departure_statistics"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    departure_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    departure_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    route_id: Mapped[int] = mapped_column(
        ForeignKey(
            "routes.route_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    bus_number: Mapped[int] = mapped_column(
        ForeignKey(
            "buses.bus_number",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    student_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    route = relationship(
        "Route",
        back_populates="departure_statistics"
    )

    bus = relationship(
        "Bus",
        back_populates="departure_statistics"
    )