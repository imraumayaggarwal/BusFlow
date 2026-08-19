from sqlalchemy.orm import Session

from app.models.student import Student
from app.models.route import Route
from app.models.user import User
from app.schemas.student import StudentUpdate


def get_student_profile(
    db: Session,
    current_user: User
):
    result = (
        db.query(Student, Route)
        .join(
            Route,
            Student.destination_id == Route.route_id
        )
        .filter(
            Student.user_id == current_user.user_id
        )
        .first()
    )

    if not result:
        raise ValueError("Student profile not found")

    student, route = result

    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "student_id": student.student_id,
        "course": student.course,
        "branch": student.branch,
        "destination_id": student.destination_id,
        "destination": route.end_location
    }


def update_student_profile(
    db: Session,
    current_user: User,
    data: StudentUpdate
):
    student = (
        db.query(Student)
        .filter(
            Student.user_id == current_user.user_id
        )
        .first()
    )

    if not student:
        raise ValueError("Student profile not found")

    # Update phone number
    if data.phone_number is not None:
        current_user.phone_number = data.phone_number

    # Update destination
    if data.destination_id is not None:

        route = (
            db.query(Route)
            .filter(
                Route.route_id == data.destination_id
            )
            .first()
        )

        if not route:
            raise ValueError("Invalid destination")

        student.destination_id = data.destination_id

    try:
        db.commit()

        return get_student_profile(
            db,
            current_user
        )

    except Exception:
        db.rollback()
        raise