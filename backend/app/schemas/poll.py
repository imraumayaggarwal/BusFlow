from enum import Enum

from pydantic import BaseModel


class PollResponse(str, Enum):
    YES = "YES"
    NO = "NO"


class PollCreate(BaseModel):
    departure_time: str


class PollResponseRequest(BaseModel):
    response: PollResponse


class PollStatusResponse(BaseModel):
    poll_id: str
    departure_time: str
    status: str


class HeadcountResponse(BaseModel):
    poll_id: str
    departure_time: str
    headcounts: dict[int, int]