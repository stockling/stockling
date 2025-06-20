from pydantic import BaseModel, EmailStr
from datetime import timezone

class UserCreate(BaseModel):
    email: str
    password: str
    password_confirm: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    
    class Config:
        from_attributes = True

class EmailCheck(BaseModel):
    email: str 