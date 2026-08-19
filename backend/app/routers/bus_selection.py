from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.orm import Session

from app.database import get_db

from app.core.dependencies import (
    get_current_user
)

from app.models.user import User

from app.schemas.bus_selection import (
    AvailableBusesResponse,
    BusSelectionRequest,
    BusSelectionResponse
)

from app.services.bus_selection import (
    get_published_buses,
    select_bus
)


router = APIRouter(
    prefix="/bus-selection",
    tags=["Bus Selection"]
)


@router.get(
    "/{poll_id}/available",
    response_model=AvailableBusesResponse
)
def available_buses(
    poll_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    try:
        return get_published_buses(
            db,
            current_user,
            poll_id
        )

    except ValueError as e:
        message = str(e)

        if message in [
            "Student profile not found",
            "Student destination not found"
        ]:
            raise HTTPException(
                status_code=404,
                detail=message
            )

        raise HTTPException(
            status_code=400,
            detail=message
        )


@router.post(
    "/{poll_id}/select",
    response_model=BusSelectionResponse
)
def select(
    poll_id: str,
    data: BusSelectionRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    try:
        return select_bus(
            db,
            current_user,
            poll_id,
            data.bus_number
        )

    except ValueError as e:
        message = str(e)

        if message in [
            "Student profile not found",
            "Student destination not found",
            "No bus assignment found",
            "Bus not found"
        ]:
            raise HTTPException(
                status_code=404,
                detail=message
            )

        if message == "Bus is full":
            raise HTTPException(
                status_code=409,
                detail=message
            )

        raise HTTPException(
            status_code=400,
            detail=message
        )