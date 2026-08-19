from datetime import datetime, timezone
from uuid import uuid4

import redis
from sqlalchemy.orm import Session

from app.models.route import Route
from app.models.student import Student
from app.models.user import User

from app.redis import redis_client
from app.schemas.poll import PollResponse


POLL_TTL = 7200


def create_poll(
    departure_time: str
):
    poll_id = (
        datetime.now(timezone.utc)
        .strftime("%Y-%m-%d")
        + ":"
        + departure_time
    )

    meta_key = f"poll:{poll_id}:meta"

    existing_poll = redis_client.exists(meta_key)

    if existing_poll:
        raise ValueError("Poll already exists")

    redis_client.hset(
        meta_key,
        mapping={
            "poll_id": poll_id,
            "departure_time": departure_time,
            "status": "OPEN"
        }
    )

    redis_client.expire(
        meta_key,
        POLL_TTL
    )

    return {
        "poll_id": poll_id,
        "departure_time": departure_time,
        "status": "OPEN"
    }


def get_poll(
    poll_id: str
):
    meta_key = f"poll:{poll_id}:meta"

    poll = redis_client.hgetall(meta_key)

    if not poll:
        raise ValueError("Poll not found")

    return poll


def respond_to_poll(
    db: Session,
    poll_id: str,
    current_user: User,
    response: PollResponse
):
    meta_key = f"poll:{poll_id}:meta"

    poll = redis_client.hgetall(meta_key)

    if not poll:
        raise ValueError("Poll not found")

    if poll.get("status") != "OPEN":
        raise ValueError("Poll is closed")

    student = (
        db.query(Student)
        .filter(
            Student.user_id == current_user.user_id
        )
        .first()
    )

    if not student:
        raise ValueError("Student profile not found")

    route = (
        db.query(Route)
        .filter(
            Route.route_id == student.destination_id
        )
        .first()
    )

    if not route:
        raise ValueError("Student destination not found")

    student_key = (
        f"poll:{poll_id}:student:"
        f"{current_user.user_id}"
    )

    headcount_key = (
        f"poll:{poll_id}:headcount:"
        f"{student.destination_id}"
    )

    result = _update_poll_response(
        student_key,
        headcount_key,
        response.value
    )

    return {
        "poll_id": poll_id,
        "student_id": current_user.user_id,
        "destination_id": student.destination_id,
        "response": response.value,
        "headcount": result
    }


def get_headcounts(
    db: Session,
    poll_id: str
):
    poll = get_poll(poll_id)

    keys = redis_client.keys(
        f"poll:{poll_id}:headcount:*"
    )

    headcounts = {}

    for key in keys:
        route_id = int(
            key.split(":")[-1]
        )

        count = redis_client.get(key)

        headcounts[route_id] = int(count or 0)

    return {
        "poll_id": poll_id,
        "departure_time": poll["departure_time"],
        "headcounts": headcounts
    }


def close_poll(
    poll_id: str
):
    meta_key = f"poll:{poll_id}:meta"

    poll = redis_client.hgetall(meta_key)

    if not poll:
        raise ValueError("Poll not found")

    redis_client.hset(
        meta_key,
        "status",
        "CLOSED"
    )

    return {
        "poll_id": poll_id,
        "departure_time": poll["departure_time"],
        "status": "CLOSED"
    }


_update_poll_response = redis_client.register_script(
    """
    local current = redis.call(
        'GET',
        KEYS[1]
    )

    local new_response = ARGV[1]

    if current == new_response then
        return tonumber(
            redis.call(
                'GET',
                KEYS[2]
            ) or '0'
        )
    end

    if current == 'YES' then
        redis.call(
            'DECR',
            KEYS[2]
        )
    end

    if new_response == 'YES' then
        redis.call(
            'INCR',
            KEYS[2]
        )
    end

    redis.call(
        'SET',
        KEYS[1],
        new_response
    )

    return tonumber(
        redis.call(
            'GET',
            KEYS[2]
        ) or '0'
    )
    """
)