from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class BusStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"


class BusCreate(BaseModel):
    bus_number: int = Field(gt=0)
    registration_number: str = Field(min_length=1, max_length=50)
    capacity: int = Field(gt=0)
    status: BusStatus = BusStatus.ACTIVE


class BusUpdate(BaseModel):
    registration_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=50
    )
    capacity: int | None = Field(
        default=None,
        gt=0
    )
    status: BusStatus | None = None


class BusResponse(BaseModel):
    bus_number: int
    registration_number: str
    capacity: int
    status: BusStatus

    model_config = ConfigDict(from_attributes=True)