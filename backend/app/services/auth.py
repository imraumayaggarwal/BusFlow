from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.models.user import User
from app.models.student import Student
from app.models.route import Route

from app.schemas.auth import StudentRegister


def register_student(
    db: Session,
    data: StudentRegister
):
    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise ValueError("Email already registered")

    # Check if selected route exists
    route = (
        db.query(Route)
        .filter(Route.route_id == data.destination_id)
        .first()
    )

    if not route:
        raise ValueError("Invalid destination")

    try:
        # Hash password
        hashed_password = hash_password(data.password)

        # Create common User record
        user = User(
            email=data.email,
            phone_number=data.phone_number,
            password_hash=hashed_password
        )

        db.add(user)

        # Generate user_id
        db.flush()

        # Create Student record
        student = Student(
            user_id=user.user_id,
            student_id=data.student_id,
            course=data.course,
            branch=data.branch,
            destination_id=data.destination_id
        )

        db.add(student)

        db.commit()

        db.refresh(user)

        return user

    except Exception:
        db.rollback()
        raise


def login_user(
    db: Session,
    email: str,
    password: str
):
    # Find user
    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise ValueError("Invalid email or password")

    # Verify password
    if not verify_password(
        password,
        user.password_hash
    ):
        raise ValueError("Invalid email or password")

    # Create JWT
    access_token = create_access_token(
        user.user_id
    )

    return access_token