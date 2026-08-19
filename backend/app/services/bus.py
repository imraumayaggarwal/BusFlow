from sqlalchemy.orm import Session

from app.models.bus import Bus
from app.schemas.bus import BusCreate, BusUpdate


def get_all_buses(db: Session):
    return (
        db.query(Bus)
        .order_by(Bus.bus_number)
        .all()
    )


def get_bus_by_number(
    db: Session,
    bus_number: int
):
    return (
        db.query(Bus)
        .filter(Bus.bus_number == bus_number)
        .first()
    )


def create_bus(
    db: Session,
    data: BusCreate
):
    existing_bus = (
        db.query(Bus)
        .filter(Bus.bus_number == data.bus_number)
        .first()
    )

    if existing_bus:
        raise ValueError("Bus number already exists")

    existing_registration = (
        db.query(Bus)
        .filter(
            Bus.registration_number
            == data.registration_number
        )
        .first()
    )

    if existing_registration:
        raise ValueError(
            "Registration number already exists"
        )

    bus = Bus(
        bus_number=data.bus_number,
        registration_number=data.registration_number,
        capacity=data.capacity,
        status=data.status
    )

    try:
        db.add(bus)
        db.commit()
        db.refresh(bus)

        return bus

    except Exception:
        db.rollback()
        raise


def update_bus(
    db: Session,
    bus_number: int,
    data: BusUpdate
):
    bus = get_bus_by_number(
        db,
        bus_number
    )

    if not bus:
        raise ValueError("Bus not found")

    if data.registration_number is not None:

        existing_registration = (
            db.query(Bus)
            .filter(
                Bus.registration_number
                == data.registration_number,
                Bus.bus_number != bus_number
            )
            .first()
        )

        if existing_registration:
            raise ValueError(
                "Registration number already exists"
            )

        bus.registration_number = (
            data.registration_number
        )

    if data.capacity is not None:
        bus.capacity = data.capacity

    if data.status is not None:
        bus.status = data.status

    try:
        db.commit()
        db.refresh(bus)

        return bus

    except Exception:
        db.rollback()
        raise