from pydantic import BaseModel, EmailStr

class StudentRegister(BaseModel):
    #user data fields
    email: EmailStr
    phone_number: str
    password : str
    #student data fields
    student_id : str
    course: str
    branch : str
    destination_id : int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class CurrentUserResponse(BaseModel):
    user_id: int
    email: EmailStr
    phone_number: str