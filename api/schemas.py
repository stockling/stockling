from pydantic import BaseModel, EmailStr
from datetime import timezone
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    
    class Config:
        from_attributes = True

class EmailCheck(BaseModel):
    email: EmailStr

class UserAccountCreate(BaseModel):
    api_key: str
    api_secret: str
    acc_no: str
    mock: bool = False

class UserAccountUpdate(BaseModel):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    acc_no: Optional[str] = None
    mock: Optional[bool] = None
    is_active: Optional[bool] = None 