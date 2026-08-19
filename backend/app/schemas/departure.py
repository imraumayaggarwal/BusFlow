from pydantic import BaseModel


class DepartureStatisticResponse(BaseModel):
    departure_id: int
    route_id: int
    bus_number: int
    departure_time: str
    capacity: int
    students_count: int


class FinalizeDepartureResponse(BaseModel):
    poll_id: str
    status: str
    statistics: list[DepartureStatisticResponse]