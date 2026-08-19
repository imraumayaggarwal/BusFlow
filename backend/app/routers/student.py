from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.student import (
    StudentResponse,
    StudentUpdate
)
from app.services.student import (
    get_student_profile,
    update_student_profile
)


router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


@router.get(
    "/me",
    response_model=StudentResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return get_student_profile(
            db,
            current_user
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.patch(
    "/me",
    response_model=StudentResponse
)
def update_my_profile(
    data: StudentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return update_student_profile(
            db,
            current_user,
            data
        )

    except ValueError as e:

        if str(e) == "Invalid destination":
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )