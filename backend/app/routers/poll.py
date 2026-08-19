from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import (
    get_current_user,
    get_current_manager
)

from app.models.user import User
from app.models.manager import Manager

from app.schemas.poll import (
    PollCreate,
    PollResponseRequest,
    PollStatusResponse,
    HeadcountResponse
)

from app.services.poll import (
    create_poll,
    get_poll,
    respond_to_poll,
    get_headcounts,
    close_poll
)


router = APIRouter(
    prefix="/polls",
    tags=["Polls"]
)


@router.post(
    "/",
    response_model=PollStatusResponse
)
def create_new_poll(
    data: PollCreate,
    current_manager: Manager = Depends(
        get_current_manager
    )
):
    try:
        return create_poll(
            data.departure_time
        )

    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )


@router.get(
    "/{poll_id}",
    response_model=PollStatusResponse
)
def get_poll_status(
    poll_id: str,
    current_user: User = Depends(
        get_current_user
    )
):
    try:
        return get_poll(
            poll_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post(
    "/{poll_id}/respond"
)
def respond(
    poll_id: str,
    data: PollResponseRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    try:
        return respond_to_poll(
            db,
            poll_id,
            current_user,
            data.response
        )

    except ValueError as e:

        message = str(e)

        if message in [
            "Poll not found",
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


@router.get(
    "/{poll_id}/headcount",
    response_model=HeadcountResponse
)
def headcount(
    poll_id: str,
    current_manager: Manager = Depends(
        get_current_manager
    ),
    db: Session = Depends(get_db)
):
    try:
        return get_headcounts(
            db,
            poll_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post(
    "/{poll_id}/close",
    response_model=PollStatusResponse
)
def close(
    poll_id: str,
    current_manager: Manager = Depends(
        get_current_manager
    )
):
    try:
        return close_poll(
            poll_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )