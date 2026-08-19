import jwt

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import decode_access_token


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )

        user = (
            db.query(User)
            .filter(User.user_id == int(user_id))
            .first()
        )

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

def get_current_manager(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    manager = (
        db.query(Manager)
        .filter(
            Manager.user_id == current_user.user_id
        )
        .first()
    )

    if manager is None:
        raise HTTPException(
            status_code=403,
            detail="Manager access required"
        )

    return manager

