import json
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.bus import Bus
from app.models.departure_statistic import DepartureStatistic
from app.models.route import Route

from app.redis import redis_client


def finalize_departure(
    db: Session,
    poll_id: str
):
    # -----------------------------------------
    # 1. Get poll metadata from Redis
    # -----------------------------------------

    poll_key = f"poll:{poll_id}:meta"

    poll = redis_client.hgetall(poll_key)

    if not poll:
        raise ValueError("Poll not found")

    # -----------------------------------------
    # 2. Get all bus assignments for this poll
    # -----------------------------------------

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

        # -------------------------------------
        # 3. Process every route assignment
        # -------------------------------------

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

            # ---------------------------------
            # 4. Validate route
            # ---------------------------------

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

            # ---------------------------------
            # 5. Process every assigned bus
            # ---------------------------------

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

                # -----------------------------
                # Get final Redis occupancy
                # -----------------------------

                occupancy_key = (
                    f"bus:{poll_id}:"
                    f"{bus_number}:occupancy"
                )

                student_count = int(
                    redis_client.get(
                        occupancy_key
                    ) or 0
                )

                # -----------------------------
                # Safety check
                # -----------------------------

                if student_count > bus.capacity:

                    raise ValueError(
                        f"Bus {bus_number} has "
                        f"invalid occupancy: "
                        f"{student_count}/"
                        f"{bus.capacity}"
                    )

                # -----------------------------
                # Parse departure time
                # -----------------------------

                departure_time = poll.get(
                    "departure_time"
                )

                if isinstance(
                    departure_time,
                    str
                ):
                    departure_time = datetime.strptime(
                        departure_time,
                        "%H:%M"
                    ).time()

                # -----------------------------
                # Create permanent record
                # -----------------------------

                statistic = DepartureStatistic(
                    departure_date=date.today(),

                    departure_time=departure_time,

                    route_id=route_id,

                    bus_number=bus_number,

                    capacity=bus.capacity,

                    student_count=student_count
                )

                db.add(statistic)

                statistics.append(
                    statistic
                )

                buses_to_cleanup.append(
                    bus_number
                )

        # -----------------------------------------
        # 6. Commit PostgreSQL
        # -----------------------------------------

        db.commit()

    except Exception:

        db.rollback()

        raise

    # -----------------------------------------
    # 7. PostgreSQL is now permanent
    #
    # Only NOW clean Redis.
    # -----------------------------------------

    for assignment_key in assignment_keys:

        redis_client.delete(
            assignment_key
        )

    # -----------------------------------------
    # 8. Delete bus occupancy
    # -----------------------------------------

    for bus_number in set(
        buses_to_cleanup
    ):

        redis_client.delete(
            f"bus:{poll_id}:"
            f"{bus_number}:occupancy"
        )

    # -----------------------------------------
    # 9. Delete poll metadata
    # -----------------------------------------

    redis_client.delete(
        poll_key
    )

    # -----------------------------------------
    # 10. Delete headcounts
    # -----------------------------------------

    headcount_keys = redis_client.keys(
        f"poll:{poll_id}:headcount:*"
    )

    if headcount_keys:

        redis_client.delete(
            *headcount_keys
        )

    # -----------------------------------------
    # 11. Delete first-poll responses
    # -----------------------------------------

    student_response_keys = redis_client.keys(
        f"poll:{poll_id}:student:*"
    )

    if student_response_keys:

        redis_client.delete(
            *student_response_keys
        )

    # -----------------------------------------
    # 12. Delete second-poll selections
    # -----------------------------------------

    selection_keys = redis_client.keys(
        f"bus-selection:{poll_id}:student:*"
    )

    if selection_keys:

        redis_client.delete(
            *selection_keys
        )

    # -----------------------------------------
    # 13. Return final statistics
    # -----------------------------------------

    return {
        "poll_id": poll_id,
        "status": "FINALIZED",
        "statistics": [
            {
                "id": statistic.id,
                "departure_date":
                    statistic.departure_date,
                "departure_time":
                    statistic.departure_time,
                "route_id":
                    statistic.route_id,
                "bus_number":
                    statistic.bus_number,
                "capacity":
                    statistic.capacity,
                "student_count":
                    statistic.student_count
            }
            for statistic in statistics
        ]
    }