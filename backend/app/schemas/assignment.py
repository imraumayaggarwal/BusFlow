from pydantic import BaseModel, Field


class BusAssignmentCreate(BaseModel):
    poll_id: str
    route_id: int
    bus_numbers: list[int] = Field(min_length=1)


class BusAssignmentResponse(BaseModel):
    poll_id: str
    route_id: int
    bus_numbers: list[int]
    total_capacity: int
    status: str


class BusOption(BaseModel):
    bus_number: int
    registration_number: str
    capacity: int
    status: str