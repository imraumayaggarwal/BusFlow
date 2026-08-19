from sqlalchemy import String, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class BusStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"


class Bus(Base):
    __tablename__ = "buses"

    bus_number: Mapped[int] = mapped_column(
        primary_key=True
    )

    registration_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[BusStatus] = mapped_column(
        Enum(BusStatus),
        nullable=False,
        default=BusStatus.ACTIVE
    )

    assignments = relationship(
        "BusAssignment",
        back_populates="bus",
        cascade="all, delete-orphan"
    )

    departure_statistics = relationship(
        "DepartureStatistic",
        back_populates="bus"
    )