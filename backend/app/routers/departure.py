from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.core.dependencies import (
    get_current_manager
)

from app.models.manager import Manager

from app.services.departure import (
    finalize_departure
)


router = APIRouter(
    prefix="/departures",
    tags=["Departures"]
)


@router.post(
    "/{poll_id}/finalize"
)
def finalize(
    poll_id: str,
    current_manager: Manager = Depends(
        get_current_manager
    ),
    db: Session = Depends(get_db)
):
    try:

        return finalize_departure(
            db,
            poll_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )