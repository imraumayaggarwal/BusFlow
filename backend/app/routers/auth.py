from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.auth import (
    StudentRegister,
    LoginRequest,
    TokenResponse,
    CurrentUserResponse
)

from app.services.auth import (
    register_student,
    login_user
)

from app.core.dependencies import get_current_user

from app.models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    data: StudentRegister,
    db: Session = Depends(get_db)
):
    try:
        user = register_student(
            db,
            data
        )

        return {
            "message": "Student registered successfully",
            "user_id": user.user_id
        }

    except ValueError as e:

        if str(e) == "Invalid destination":
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

        raise HTTPException(
            status_code=409,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    try:
        access_token = login_user(
            db,
            data.email,
            data.password
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )


@router.get(
    "/me",
    response_model=CurrentUserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "phone_number": current_user.phone_number
    }