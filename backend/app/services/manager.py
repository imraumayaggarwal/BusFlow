from sqlalchemy.orm import Session

from app.models.manager import Manager
from app.models.user import User


def get_manager_profile(
    db: Session,
    current_manager: Manager
):
    user = (
        db.query(User)
        .filter(
            User.user_id == current_manager.user_id
        )
        .first()
    )

    if not user:
        raise ValueError("User profile not found")

    return {
        "user_id": current_manager.user_id,
        "manager_id": current_manager.manager_id,
        "email": user.email,
        "phone_number": user.phone_number
    }