from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import get_current_manager
from app.models.manager import Manager
from app.schemas.manager import ManagerResponse
from app.services.manager import get_manager_profile


router = APIRouter(
    prefix="/managers",
    tags=["Managers"]
)


@router.get(
    "/me",
    response_model=ManagerResponse
)
def get_my_manager_profile(
    current_manager: Manager = Depends(get_current_manager),
    db: Session = Depends(get_db)
):
    try:
        return get_manager_profile(
            db,
            current_manager
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )