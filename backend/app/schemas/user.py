from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    employee_id: str


class UserCreate(UserBase):
    is_admin: bool = False
    password: Optional[str] = None


class UserResponse(UserBase):
    id: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminLoginRequest(BaseModel):
    employee_id: str
    password: str


class VisitorLoginRequest(BaseModel):
    employee_id: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_admin: bool


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[TokenResponse] = None
