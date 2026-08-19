from pydantic import BaseModel, EmailStr


class ManagerResponse(BaseModel):
    user_id: int
    manager_id: str
    email: EmailStr
    phone_number: str