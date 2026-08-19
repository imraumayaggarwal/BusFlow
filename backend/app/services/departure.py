import json

from sqlalchemy.orm import Session

from app.models.bus import Bus
from app.models.departure_statistic import DepartureStatistic
from app.models.route import Route

from app.redis import redis_client


def finalize_departure(
    db: Session,
    poll_id: str
):
    poll_key = f"poll:{poll_id}:meta"

    poll = redis_client.hgetall(poll_key)

    if not poll:
        raise ValueError("Poll not found")

    assignment_keys = redis_client.keys(
        f"assignment:{poll_id}:*"
    )

    if not assignment_keys:
        raise ValueError(
            "No bus assignments found"
        )

    statistics = []
    buses_to_cleanup = []

    try:

        for assignment_key in assignment_keys:

            raw_assignment = redis_client.get(
                assignment_key
            )

            if not raw_assignment:
                continue

            assignment = json.loads(
                raw_assignment
            )

            if assignment.get("status") != "PUBLISHED":
                raise ValueError(
                    "All bus assignments must be published"
                )

            route_id = assignment["route_id"]

            bus_numbers = assignment[
                "bus_numbers"
            ]

            route = (
                db.query(Route)
                .filter(
                    Route.route_id == route_id
                )
                .first()
            )

            if not route:
                raise ValueError(
                    f"Route {route_id} not found"
                )

            for bus_number in bus_numbers:

                bus = (
                    db.query(Bus)
                    .filter(
                        Bus.bus_number == bus_number
                    )
                    .first()
                )

                if not bus:
                    raise ValueError(
                        f"Bus {bus_number} not found"
                    )

                occupancy_key = (
                    f"bus:{poll_id}:"
                    f"{bus_number}:occupancy"
                )

                students_count = int(
                    redis_client.get(
                        occupancy_key
                    ) or 0
                )

                if students_count > bus.capacity:
                    raise ValueError(
                        f"Bus {bus_number} has "
                        f"invalid occupancy"
                    )

                statistic = DepartureStatistic(
                    route_id=route_id,
                    bus_number=bus_number,
                    departure_time=poll[
                        "departure_time"
                    ],
                    capacity=bus.capacity,
                    students_count=students_count
                )

                db.add(statistic)

                statistics.append(
                    statistic
                )

                buses_to_cleanup.append(
                    bus_number
                )

        db.commit()

    except Exception:
        db.rollback()
        raise

    # -----------------------------------------
    # PostgreSQL commit succeeded.
    # Now Redis can be cleaned.
    # -----------------------------------------

    for assignment_key in assignment_keys:
        redis_client.delete(
            assignment_key
        )

    for bus_number in buses_to_cleanup:

        redis_client.delete(
            f"bus:{poll_id}:"
            f"{bus_number}:occupancy"
        )

    redis_client.delete(
        poll_key
    )

    headcount_keys = redis_client.keys(
        f"poll:{poll_id}:headcount:*"
    )

    if headcount_keys:
        redis_client.delete(
            *headcount_keys
        )

    student_response_keys = redis_client.keys(
        f"poll:{poll_id}:student:*"
    )

    if student_response_keys:
        redis_client.delete(
            *student_response_keys
        )

    selection_keys = redis_client.keys(
        f"bus-selection:{poll_id}:student:*"
    )

    if selection_keys:
        redis_client.delete(
            *selection_keys
        )

    return {
        "poll_id": poll_id,
        "status": "FINALIZED",
        "statistics": [
            {
                "departure_id":
                    statistic.departure_id,
                "route_id":
                    statistic.route_id,
                "bus_number":
                    statistic.bus_number,
                "departure_time":
                    statistic.departure_time,
                "capacity":
                    statistic.capacity,
                "students_count":
                    statistic.students_count
            }
            for statistic in statistics
        ]
    }