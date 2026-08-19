from typing import Optional

from pydantic import BaseModel, EmailStr


class StudentResponse(BaseModel):
    user_id: int
    email: EmailStr
    phone_number: str

    student_id: str
    course: str
    branch: str

    destination_id: int
    destination: str


class StudentUpdate(BaseModel):
    phone_number: Optional[str] = None
    destination_id: Optional[int] = None