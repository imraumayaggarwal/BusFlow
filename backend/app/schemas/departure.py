from datetime import date, time

from pydantic import BaseModel


class DepartureStatisticResponse(BaseModel):
    id: int
    departure_date: date
    departure_time: time
    route_id: int
    bus_number: int
    capacity: int
    student_count: int


class FinalizeDepartureResponse(BaseModel):
    poll_id: str
    status: str
    statistics: list[DepartureStatisticResponse]