from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BusAssignment(Base):
    __tablename__ = "bus_assignments"

    bus_number: Mapped[int] = mapped_column(
        ForeignKey(
            "buses.bus_number",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    route_id: Mapped[int] = mapped_column(
        ForeignKey(
            "routes.route_id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    bus = relationship(
        "Bus",
        back_populates="assignments"
    )

    route = relationship(
        "Route",
        back_populates="assignments"
    )