from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.database import get_db 
from app.schemas.route_response import RouteResponse
from app.services.route_response import get_all_routes

router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)

@router.get(
    "/",
    response_model= list[RouteResponse]
)
def get_routes(
    db: Session = Depends(get_db)
):
    return get_all_routes(db)
