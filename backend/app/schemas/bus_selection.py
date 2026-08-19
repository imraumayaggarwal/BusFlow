from pydantic import BaseModel


class AvailableBus(BaseModel):
    bus_number: int
    registration_number: str
    capacity: int
    occupied: int
    available_seats: int


class AvailableBusesResponse(BaseModel):
    poll_id: str
    route_id: int
    buses: list[AvailableBus]


class BusSelectionRequest(BaseModel):
    bus_number: int


class BusSelectionResponse(BaseModel):
    poll_id: str
    route_id: int
    bus_number: int
    message: str
    occupied: int
    available_seats: int