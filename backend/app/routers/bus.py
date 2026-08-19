from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.core.dependencies import get_current_manager

from app.models.manager import Manager

from app.schemas.bus import (
    BusCreate,
    BusUpdate,
    BusResponse
)

from app.services.bus import (
    get_all_buses,
    get_bus_by_number,
    create_bus,
    update_bus
)


router = APIRouter(
    prefix="/buses",
    tags=["Buses"]
)


@router.get(
    "/",
    response_model=list[BusResponse]
)
def get_buses(
    current_manager: Manager = Depends(
        get_current_manager
    ),
    db: Session = Depends(get_db)
):
    return get_all_buses(db)


@router.get(
    "/{bus_number}",
    response_model=BusResponse
)
def get_bus(
    bus_number: int,
    current_manager: Manager = Depends(
        get_current_manager
    ),
    db: Session = Depends(get_db)
):
    bus = get_bus_by_number(
        db,
        bus_number
    )

    if not bus:
        raise HTTPException(
            status_code=404,
            detail="Bus not found"
        )

    return bus


@router.post(
    "/",
    response_model=BusResponse,
    status_code=201
)
def create_new_bus(
    data: BusCreate,
    current_manager: Manager = Depends(
        get_current_manager
    ),
    db: Session = Depends(get_db)
):
    try:
        return create_bus(
            db,
            data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )


@router.patch(
    "/{bus_number}",
    response_model=BusResponse
)
def update_existing_bus(
    bus_number: int,
    data: BusUpdate,
    current_manager: Manager = Depends(
        get_current_manager
    ),
    db: Session = Depends(get_db)
):
    try:
        return update_bus(
            db,
            bus_number,
            data
        )

    except ValueError as e:

        if str(e) == "Bus not found":
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

        raise HTTPException(
            status_code=409,
            detail=str(e)
        )