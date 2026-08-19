from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)
from sqlalchemy.orm import Session

from app.database import get_db

from app.core.dependencies import (
    get_current_user,
    get_current_manager
)

from app.models.user import User
from app.models.manager import Manager

from app.schemas.assignment import (
    BusAssignmentCreate,
    BusAssignmentResponse,
    BusOption
)

from app.services.assignment import (
    get_available_buses,
    create_assignment,
    publish_assignment,
    get_assignment
)


router = APIRouter(
    prefix="/assignments",
    tags=["Bus Assignments"]
)


@router.get(
    "/available/{route_id}",
    response_model=list[BusOption]
)
def available_buses(
    route_id: int,
    current_manager: Manager = Depends(
        get_current_manager
    ),
    db: Session = Depends(get_db)
):
    try:
        buses = get_available_buses(
            db,
            route_id
        )

        return buses

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post(
    "/",
    response_model=BusAssignmentResponse
)
def assign_buses(
    data: BusAssignmentCreate,
    current_manager: Manager = Depends(
        get_current_manager
    ),
    db: Session = Depends(get_db)
):
    try:
        return create_assignment(
            db=db,
            poll_id=data.poll_id,
            route_id=data.route_id,
            bus_numbers=data.bus_numbers
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post(
    "/{poll_id}/{route_id}/publish",
    response_model=BusAssignmentResponse
)
def publish(
    poll_id: str,
    route_id: int,
    current_manager: Manager = Depends(
        get_current_manager
    )
):
    try:
        return publish_assignment(
            poll_id,
            route_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/{poll_id}/{route_id}",
    response_model=BusAssignmentResponse
)
def assignment(
    poll_id: str,
    route_id: int,
    current_user: User = Depends(
        get_current_user
    )
):
    try:
        return get_assignment(
            poll_id,
            route_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )