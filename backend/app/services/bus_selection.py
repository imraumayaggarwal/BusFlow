import json

from sqlalchemy.orm import Session

from app.models.bus import Bus
from app.models.student import Student
from app.models.route import Route
from app.models.user import User

from app.redis import redis_client


def get_student_route(
    db: Session,
    current_user: User
):
    student = (
        db.query(Student)
        .filter(
            Student.user_id == current_user.user_id
        )
        .first()
    )

    if not student:
        raise ValueError(
            "Student profile not found"
        )

    route = (
        db.query(Route)
        .filter(
            Route.route_id == student.destination_id
        )
        .first()
    )

    if not route:
        raise ValueError(
            "Student destination not found"
        )

    return student, route


def get_published_buses(
    db: Session,
    current_user: User,
    poll_id: str
):
    student, route = get_student_route(
        db,
        current_user
    )

    assignment_key = (
        f"assignment:{poll_id}:"
        f"{route.route_id}"
    )

    raw_assignment = redis_client.get(
        assignment_key
    )

    if not raw_assignment:
        raise ValueError(
            "No bus assignment found"
        )

    assignment = json.loads(
        raw_assignment
    )

    if assignment.get("status") != "PUBLISHED":
        raise ValueError(
            "Bus assignment has not been published"
        )

    bus_numbers = assignment.get(
        "bus_numbers",
        []
    )

    if not bus_numbers:
        raise ValueError(
            "No buses assigned"
        )

    buses = (
        db.query(Bus)
        .filter(
            Bus.bus_number.in_(bus_numbers)
        )
        .all()
    )

    result = []

    for bus in buses:

        occupancy_key = (
            f"bus:{poll_id}:"
            f"{bus.bus_number}:occupancy"
        )

        occupied = int(
            redis_client.get(
                occupancy_key
            ) or 0
        )

        result.append(
            {
                "bus_number": bus.bus_number,
                "registration_number":
                    bus.registration_number,
                "capacity": bus.capacity,
                "occupied": occupied,
                "available_seats":
                    max(
                        bus.capacity - occupied,
                        0
                    )
            }
        )

    return {
        "poll_id": poll_id,
        "route_id": route.route_id,
        "buses": result
    }


def select_bus(
    db: Session,
    current_user: User,
    poll_id: str,
    bus_number: int
):
    student, route = get_student_route(
        db,
        current_user
    )

    assignment_key = (
        f"assignment:{poll_id}:"
        f"{route.route_id}"
    )

    raw_assignment = redis_client.get(
        assignment_key
    )

    if not raw_assignment:
        raise ValueError(
            "No bus assignment found"
        )

    assignment = json.loads(
        raw_assignment
    )

    if assignment.get("status") != "PUBLISHED":
        raise ValueError(
            "Bus assignment has not been published"
        )

    assigned_buses = assignment.get(
        "bus_numbers",
        []
    )

    if bus_number not in assigned_buses:
        raise ValueError(
            "This bus is not assigned to your destination"
        )

    bus = (
        db.query(Bus)
        .filter(
            Bus.bus_number == bus_number
        )
        .first()
    )

    if not bus:
        raise ValueError(
            "Bus not found"
        )

    student_bus_key = (
        f"bus-selection:{poll_id}:"
        f"student:{current_user.user_id}"
    )

    occupancy_key = (
        f"bus:{poll_id}:"
        f"{bus_number}:occupancy"
    )

    current_selection = redis_client.get(
        student_bus_key
    )

    if current_selection == str(bus_number):
        occupied = int(
            redis_client.get(
                occupancy_key
            ) or 0
        )

        return {
            "poll_id": poll_id,
            "route_id": route.route_id,
            "bus_number": bus_number,
            "message": "Bus already selected",
            "occupied": occupied,
            "available_seats":
                max(
                    bus.capacity - occupied,
                    0
                )
        }

    if current_selection:
        raise ValueError(
            "You have already selected a bus"
        )

    result = reserve_bus_seat(
        student_bus_key,
        occupancy_key,
        bus.capacity,
        current_user.user_id,
        bus_number
    )

    if result == -1:
        raise ValueError(
            "Bus is full"
        )

    return {
        "poll_id": poll_id,
        "route_id": route.route_id,
        "bus_number": bus_number,
        "message": "Bus selected successfully",
        "occupied": result,
        "available_seats":
            bus.capacity - result
    }


reserve_bus_seat = redis_client.register_script(
    """
    local student_key = KEYS[1]
    local occupancy_key = KEYS[2]

    local capacity = tonumber(ARGV[1])
    local bus_number = ARGV[2]

    local existing_bus = redis.call(
        'GET',
        student_key
    )

    if existing_bus then
        return -2
    end

    local occupied = tonumber(
        redis.call(
            'GET',
            occupancy_key
        ) or '0'
    )

    if occupied >= capacity then
        return -1
    end

    occupied = redis.call(
        'INCR',
        occupancy_key
    )

    redis.call(
        'SET',
        student_key,
        bus_number
    )

    return occupied
    """
)